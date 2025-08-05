#!/bin/bash

# Valideringsscript for SkyForskning.no admin panel
# Dato: 2025-08-04

echo "Kjører enkel validering av JavaScript-filer..."

# Sjekk om API_BASE_URL er korrekt i config.js
if grep -q "API_BASE_URL.*skyforskning.no/api/v1" /home/skyforskning.no/forskning/admin_template/js/admin/config.js; then
    echo "✓ API_BASE_URL er korrekt konfigurert"
    exit 0
else
    echo "✗ API_BASE_URL er mulig feil konfigurert i config.js"
    exit 1
fi
