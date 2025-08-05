# SkyForskning.no Admin Panel Deploy Guide

Dette dokumentet beskriver korrekt oppsett og deployment av admin-panelet for SkyForskning.no.

## Viktige stier

**ALLE OFFENTLIG TILGJENGELIGE FILER SKAL PLASSERES I:**
- `/home/skyforskning.no/public_html`
- `/home/skyforskning.no/public_html/admin`
- `/home/skyforskning.no/public_html/js`
- `/home/skyforskning.no/public_html/css`

**MERK:** Ikke bruk andre stier som `/home/skyforskning.no/prod` for offentlig tilgjengelige filer.

## Scripter for deploy og feilsøking

Det er opprettet tre hovedscripter for å administrere admin-panelet:

### 1. Deploy script (`deploy_correct.sh`)

Dette scriptet håndterer full deploy av admin-panelet til korrekte stier i `public_html`:

```bash
./deploy_correct.sh
```

Scriptet vil:
- Validere alle kildefiler
- Opprette riktig mappestruktur i `public_html`
- Kopiere og tilpasse filer med absolutte stier
- Opprette `.htaccess`-filer for korrekte MIME-typer
- Verifisere at alle nødvendige elementer er på plass

### 2. MIME-type fikser (`fix_mime_public_html.sh`)

Dette scriptet fokuserer spesifikt på å fikse MIME-type problemer:

```bash
./fix_mime_public_html.sh
```

Scriptet vil:
- Opprette `.htaccess`-filer for riktige MIME-typer
- Korrigere stier i eksisterende filer
- Sette korrekte filrettigheter
- Opprette en test-HTML-fil for å verifisere MIME-typer

### 3. Diagnostiseringsverktøy

For å diagnostisere potensielle problemer, kjør diagnostiseringsverktøyet:

```bash
./diagnose.sh
```

## Riktig mappestruktur

```
/home/skyforskning.no/public_html/
├── admin/
│   └── index.html
├── js/
│   ├── admin/
│   │   ├── api-client.js
│   │   ├── auth.js
│   │   ├── config.js
│   │   ├── ui-manager.js
│   │   └── views/
│   │       ├── dashboard.js
│   │       ├── login.js
│   │       ├── logs.js
│   │       ├── system-settings.js
│   │       └── user-management.js
└── css/
    └── admin-style.css
```

## Korrekt sti-konfigurering

1. I `ui-manager.js` skal modulstier være absolutte:
   ```javascript
   const modulePath = `/js/admin/views/${viewName}.js`;
   ```

2. I `index.html` skal script og CSS-referanser være absolutte:
   ```html
   <link rel="stylesheet" href="/css/admin-style.css">
   <script src="/js/admin/config.js"></script>
   ```

## Feilsøking MIME-type problemer

Hvis du fortsatt opplever MIME-type problemer, verifiser følgende:

1. Åpne `https://skyforskning.no/mime-test.html` i nettleseren
2. Sjekk om testene viser suksess for både JavaScript og CSS
3. Tøm nettleserens cache eller prøv i Incognito/Private mode

## Viktige tips

- Bruk alltid **absolutte stier** (starter med `/`) i produksjonsmiljøet
- Bruk `.htaccess`-filer for å sikre korrekte MIME-typer
- Alle filer må ha riktige leserettigheter (644 for filer, 755 for mapper)
- Verifiser at webserveren er konfigurert til å servere `.js`-filer som `application/javascript`

## Troubleshooting

Hvis du fortsatt opplever problemer:

1. Kjør `fix_mime_public_html.sh` for å fikse MIME-type problemer
2. Verifiser at webserveren har `mod_headers` aktivert
3. Sjekk at `.htaccess`-filer er aktivert i webserver-konfigurasjonen
4. Sjekk nettleserkonsollen (F12) for detaljer om feilene

## Kontaktinformasjon

Ved problemer eller spørsmål, kontakt:
- E-post: support@skyforskning.no
