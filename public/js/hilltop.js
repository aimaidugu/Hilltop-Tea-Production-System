/**
 * hilltop.js — Hilltop Tea frontend component library.
 * All Alpine.js components and Chart.js initialisers live here.
 */

'use strict';

// ── Wage tier constants (mirrors Python PRODUCTION_TIERS exactly) ──────────
const PRODUCTION_TIERS = [[0, 349, 250], [350, 399, 270], [400, 499, 300], [500, Infinity, 320]];
const WRAPPING_RATE = 100;

/**
 * wageRow(group)
 * Alpine.js component for a single employee row in the production entry table.
 * Provides real-time wage calculation as carton count changes.
 *
 * @param {string} group - 'production' or 'wrapping'
 * @returns {object} Alpine.js component data object
 */
function wageRow(group) {
    return {
        cartons: 0,
        group: group,
        get wage() {
            const n = Number(this.cartons);
            if (!Number.isInteger(n) || n < 0) return 0;
            if (this.group === 'wrapping') return n * WRAPPING_RATE;
            for (const [low, high, rate] of PRODUCTION_TIERS) {
                if (n >= low && n <= high) return n * rate;
            }
            return 0;
        },
        get wageFormatted() {
            return '₦' + this.wage.toLocaleString('en-NG', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
        },
    };
}

/**
 * flashMessage()
 * Alpine.js component for auto-dismissing flash messages.
 * Fades out after 5 seconds, can be dismissed manually.
 */
function flashMessage() {
    return {
        show: true,
        init() {
            setTimeout(() => { this.show = false; }, 5000);
        },
    };
}

/**
 * paymentModal(employeeId, employeeName, monthStr)
 * Alpine.js component for the record-payment modal on payroll page.
 */
function paymentModal() {
    return {
        open: false,
        employeeId: null,
        employeeName: '',
        monthStr: '',
        openFor(id, name, month) {
            this.employeeId = id;
            this.employeeName = name;
            this.monthStr = month;
            this.open = true;
        },
        close() { this.open = false; },
    };
}

/**
 * navDropdown()
 * Alpine.js component for user menu dropdown in navbar.
 */
function navDropdown() {
    return {
        open: false,
        toggle() { this.open = !this.open; },
        close() { this.open = false; },
    };
}

// ── Chart.js initialisers ──────────────────────────────────────────────────
// Called from per-page {% block charts_js %} blocks.
// Data is injected by Flask as JSON in the template.

/**
 * initWageSplitChart(canvasId, labels, data)
 * Donut chart: production vs wrapping wage split.
 */
function initWageSplitChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#1e3932', '#c9a96e'],
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { font: { family: 'DM Sans' } } },
            },
        },
    });
}

/**
 * initDailyCartonsChart(canvasId, labels, data)
 * Bar chart: daily carton output over last 14 days.
 */
function initDailyCartonsChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cartons',
                data: data,
                backgroundColor: '#1e3932',
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true, ticks: { font: { family: 'DM Mono' } } },
                x: { ticks: { font: { family: 'DM Sans' } } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

/**
 * initMonthlyTrendChart(canvasId, labels, data)
 * Line chart: monthly total wages over last 6 months.
 */
function initMonthlyTrendChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Wages (₦)',
                data: data,
                borderColor: '#c9a96e',
                backgroundColor: 'rgba(201,169,110,0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#1e3932',
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        font: { family: 'DM Mono' },
                        callback: v => '₦' + v.toLocaleString('en-NG'),
                    },
                },
                x: { ticks: { font: { family: 'DM Sans' } } },
            },
        },
    });
}
