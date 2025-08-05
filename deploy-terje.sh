#!/bin/sh
# deploy-terje.sh - Canonical deploy script for SkyForskning.no
# Copies all changed HTML/JS/CSS files to the correct public_html and admin directories
# Always use this for deployment!

set -e

SOURCE_DIR="/home/skyforskning.no/forskning/admin_template"
PUBLIC_HTML="/home/skyforskning.no/public_html"
ADMIN_DIR="$PUBLIC_HTML/admin"
JS_DIR="$PUBLIC_HTML/js"
CSS_DIR="$PUBLIC_HTML/css"


# Parse options
MODE="all"
if [ "$1" = "--admin" ]; then
  MODE="admin"
elif [ "$1" = "--front" ]; then
  MODE="front"
fi

# Ensure directory structure
mkdir -p "$ADMIN_DIR"
mkdir -p "$JS_DIR/admin/views"
mkdir -p "$CSS_DIR"

copy_admin() {
  # Copy admin CSS
  cp "$SOURCE_DIR/css/admin-style.css" "$CSS_DIR/"

  # Copy admin JS files
  cp "$SOURCE_DIR/js/admin/config.js" "$JS_DIR/admin/"
  cp "$SOURCE_DIR/js/admin/api-client.js" "$JS_DIR/admin/"
  cp "$SOURCE_DIR/js/admin/auth.js" "$JS_DIR/admin/"
  cp "$SOURCE_DIR/js/admin/ui-manager.js" "$JS_DIR/admin/"
  cp "$SOURCE_DIR/js/admin/main.js" "$JS_DIR/admin/"
  cp "$SOURCE_DIR/js/admin/views/"*.js "$JS_DIR/admin/views/"

  # Copy admin HTML
  cp "$SOURCE_DIR/vue_admin_mount.html" "$ADMIN_DIR/index.html"

  # Fix references in ui-manager.js if needed
  sed -i 's|const modulePath = `../js/admin/views/${viewName}.js`;|const modulePath = `/js/admin/views/${viewName}.js`;|g' "$JS_DIR/admin/ui-manager.js"

  # Fix CSS/JS references in HTML if needed
  sed -i -e 's|href="../css/admin-style.css"|href="/css/admin-style.css"|g' \
         -e 's|src="../js/admin/config.js"|src="/js/admin/config.js"|g' \
         "$ADMIN_DIR/index.html"
}

copy_front() {
  # Placeholder: Add frontend copy commands here if needed
  echo "[deploy-terje.sh] (front) No frontend copy implemented yet."
}

# Main copy logic
if [ "$MODE" = "all" ]; then
  copy_admin
  copy_front
elif [ "$MODE" = "admin" ]; then
  copy_admin
elif [ "$MODE" = "front" ]; then
  copy_front
fi


# Restart Gunicorn (adjust service name as needed)
echo "[deploy-terje.sh] Restarting Gunicorn..."
sudo systemctl restart gunicorn || {
  echo "[deploy-terje.sh] ERROR: Gunicorn restart failed!" >&2
  exit 1
}

# Verify Gunicorn is running
sleep 2
if systemctl is-active --quiet gunicorn; then
  echo "[deploy-terje.sh] Gunicorn is running. Deployment successful."
else
  echo "[deploy-terje.sh] ERROR: Gunicorn is NOT running after restart!" >&2
  exit 1
fi

echo "[deploy-terje.sh] Deployment complete. Files copied to $PUBLIC_HTML and $ADMIN_DIR."
