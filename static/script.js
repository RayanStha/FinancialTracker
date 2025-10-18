// Custom JavaScript for Investment Planner

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add loading states to buttons
    $('button[type="submit"]').click(function() {
        var $btn = $(this);
        var originalText = $btn.html();
        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i>Loading...');
        
        // Re-enable after 3 seconds as fallback
        setTimeout(function() {
            $btn.prop('disabled', false).html(originalText);
        }, 3000);
    });

    // Format currency inputs
    $('input[type="number"][step="0.01"]').on('blur', function() {
        var value = parseFloat($(this).val());
        if (!isNaN(value)) {
            $(this).val(value.toFixed(2));
        }
    });

    // Format share inputs
    $('input[type="number"][step="0.0001"]').on('blur', function() {
        var value = parseFloat($(this).val());
        if (!isNaN(value)) {
            $(this).val(value.toFixed(4));
        }
    });

    // Add confirmation for destructive actions
    $('.btn-danger').click(function(e) {
        if (!confirm('Are you sure you want to perform this action?')) {
            e.preventDefault();
        }
    });

    // Auto-refresh data every 5 minutes
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            refreshDataQuietly();
        }
    }, 300000); // 5 minutes
});

// Global functions
function refreshData() {
    showLoadingSpinner();
    
    fetch('/api/refresh_data')
    .then(response => response.json())
    .then(data => {
        hideLoadingSpinner();
        if (data.success) {
            showAlert('Data refreshed successfully', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('Error refreshing data: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoadingSpinner();
        console.error('Error:', error);
        showAlert('An error occurred while refreshing data', 'danger');
    });
}

function refreshDataQuietly() {
    fetch('/api/refresh_data')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Data refreshed quietly');
        }
    })
    .catch(error => {
        console.error('Quiet refresh error:', error);
    });
}

function showAlert(message, type) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').first().prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

function showLoadingSpinner() {
    if ($('#loadingSpinner').length === 0) {
        var spinnerHtml = `
            <div id="loadingSpinner" class="position-fixed top-50 start-50 translate-middle" style="z-index: 9999;">
                <div class="bg-white p-4 rounded shadow">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 mb-0">Loading...</p>
                    </div>
                </div>
            </div>
        `;
        $('body').append(spinnerHtml);
    }
    $('#loadingSpinner').show();
}

function hideLoadingSpinner() {
    $('#loadingSpinner').hide();
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

function formatNumber(value, decimals = 2) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

// API helper functions
function apiCall(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Portfolio management functions
function addHolding(ticker, companyName, shares, avgCost, category) {
    return apiCall('/api/add_holding', 'POST', {
        ticker: ticker,
        company_name: companyName,
        shares: shares,
        avg_cost: avgCost,
        category: category
    });
}

function updateHolding(ticker, shares, avgCost) {
    return apiCall('/api/update_holding', 'POST', {
        ticker: ticker,
        shares: shares,
        avg_cost: avgCost
    });
}

function updateContribution(contribution) {
    return apiCall('/api/update_contribution', 'POST', {
        contribution: contribution
    });
}

// Stock research functions
function getStockInfo(ticker) {
    return apiCall(`/api/stock_info/${ticker}`);
}

// Export functions
function exportExcel() {
    window.location.href = '/api/export_excel';
}

// Keyboard shortcuts
$(document).keydown(function(e) {
    // Ctrl+R or Cmd+R to refresh data
    if ((e.ctrlKey || e.metaKey) && e.keyCode === 82) {
        e.preventDefault();
        refreshData();
    }
    
    // Ctrl+E or Cmd+E to export Excel
    if ((e.ctrlKey || e.metaKey) && e.keyCode === 69) {
        e.preventDefault();
        exportExcel();
    }
});

// Handle URL parameters for research page
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Initialize page-specific functionality
$(document).ready(function() {
    // Research page: auto-search if ticker parameter is present
    if (window.location.pathname === '/research') {
        var ticker = getUrlParameter('ticker');
        if (ticker) {
            $('#stockSearch').val(ticker);
            setTimeout(() => searchSpecificStock(ticker), 500);
        }
    }
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'danger');
});

// Service worker registration for offline functionality (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/static/sw.js')
        //     .then(function(registration) {
        //         console.log('ServiceWorker registration successful');
        //     })
        //     .catch(function(err) {
        //         console.log('ServiceWorker registration failed');
        //     });
    });
}
