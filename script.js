// Test data from Excel
const testData = [
    { company: "SBC International Services", designation: "Founder & CMO" },
    { company: "Bici e Vacanze", designation: "Founder" },
    { company: "Exped Tribe GmbH", designation: "Founder, Director" },
    { company: "Lions Sports Travel", designation: "CEO" },
    { company: "Reviva", designation: "Ceo" },
    { company: "Lobagola MotoTours", designation: "Founder" },
    { company: "SixEmotions - Travel Lifestyle", designation: "Co-Founder" },
    { company: "A2A YACHTING", designation: "YACHT CHARTER & SALES DIRECTOR" },
    { company: "Essence of Italy", designation: "Co-Owner & Sales Director" },
    { company: "#ViajaAgora", designation: "CEO | Sales Manager" },
    { company: "Béchamels", designation: "Founder & CEO" },
    { company: "Grand Hotel Bohemia", designation: "Director of Sales" },
    { company: "Ionian Estates and Villas Limited", designation: "Operations Director" },
    { company: "EscapeTours", designation: "Founder EscapeTours" },
    { company: "PlanUGo", designation: "CEO & Founder" },
    { company: "Extol Inn", designation: "Sales Manager" },
    { company: "Sentima", designation: "Founder" },
    { company: "Grecia365 di Karlitalia Tour Operator Srl", designation: "CEO & CO-FOUNDER" },
    { company: "Catalonia Hotels & Resorts", designation: "International Sales Director" },
    { company: "MEININGER Hotels", designation: "Head of Financial Reporting" },
    { company: "FareHarbor", designation: "Senior Strategic Partnerships Manager" },
    { company: "Holiday Extras", designation: "Commercial Partnerships Lead" },
    { company: "SkiStar AB", designation: "Production Manager" },
    { company: "PONANT", designation: "Chief Executive Officer, Americas" },
    { company: "Thorpe Park", designation: "Head of Partnerships, Events and VIP" },
    { company: "Lighthouse", designation: "Senior Business Development Manager" },
    { company: "FareHarbor", designation: "Senior Account Executive, Mid Market" },
    { company: "Relais & Châteaux", designation: "Delegation Manager & Sales Greater China" },
    { company: "Quintessentially Belux", designation: "Partnerships Manager" },
    { company: "Kuoni Group", designation: "Senior Group Sales Manager for Israel, Sweden, Switzeralnd and Iceland" }
];

// API endpoint (update with your backend URL)
const API_URL = 'http://localhost:5000/search';

// Populate test data dropdown
function populateTestData() {
    const select = document.getElementById('testDataSelect');
    
    testData.forEach((item, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${item.company} - ${item.designation}`;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        if (e.target.value) {
            const selected = testData[e.target.value];
            document.getElementById('company').value = selected.company;
            document.getElementById('designation').value = selected.designation;
        }
    });
}

// Handle form submission
async function handleSearch(event) {
    event.preventDefault();
    
    const company = document.getElementById('company').value.trim();
    const designation = document.getElementById('designation').value.trim();
    
    if (!company || !designation) {
        showError('Please enter both company and designation');
        return;
    }
    
    // Show loading state
    const searchBtn = document.getElementById('searchBtn');
    const btnText = searchBtn.querySelector('.btn-text');
    const spinner = searchBtn.querySelector('.loading-spinner');
    
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    searchBtn.disabled = true;
    
    // Hide previous results/errors
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ company, designation })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.person, data.sources_used);
        } else {
            showError(data.error || 'No results found');
        }
    } catch (error) {
        showError('Error connecting to server. Make sure the backend is running.');
        console.error('Error:', error);
    } finally {
        // Hide loading state
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
        searchBtn.disabled = false;
    }
}

// Display results
function displayResults(person, sourcesUsed) {
    const resultsDiv = document.getElementById('results');
    
    resultsDiv.innerHTML = `
        <div class="person-info">
            <h3>🎯 Person Found</h3>
            
            <div class="info-row">
                <span class="info-label">First Name:</span>
                <span class="info-value">${person.first_name}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Last Name:</span>
                <span class="info-value">${person.last_name}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Title:</span>
                <span class="info-value">${person.current_title}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Confidence:</span>
                <span class="info-value">${Math.round(person.confidence * 100)}%</span>
            </div>
            
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${person.confidence * 100}%"></div>
            </div>
            
            <div class="info-row">
                <span class="info-label">Source URL:</span>
                <span class="info-value">
                    <a href="${person.source_url}" target="_blank">${person.source_url}</a>
                </span>
            </div>
            
            <div class="info-row">
                <span class="info-label">Sources Used:</span>
                <span class="info-value">${sourcesUsed}</span>
            </div>
        </div>
    `;
    
    document.getElementById('resultsSection').style.display = 'block';
}

// Show error
function showError(message) {
    const errorDiv = document.querySelector('.error-card');
    errorDiv.textContent = message;
    document.getElementById('errorSection').style.display = 'block';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    populateTestData();
    
    const form = document.getElementById('searchForm');
    form.addEventListener('submit', handleSearch);
});