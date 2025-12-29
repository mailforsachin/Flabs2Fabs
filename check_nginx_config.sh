#!/bin/bash

echo "=== NGINX Configuration Analysis ==="
echo

echo "1. NGINX Status:"
sudo systemctl status nginx --no-pager | head -20
echo

echo "2. NGINX Process Info:"
sudo ps aux | grep nginx | grep -v grep
echo

echo "3. NGINX Configuration Test:"
sudo nginx -t
echo

echo "4. Main Configuration File:"
sudo nginx -T 2>/dev/null | grep -A5 "configuration file" || echo "Could not determine config file"
echo

echo "5. All Server Blocks:"
echo "Checking /etc/nginx/sites-available/:"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "Directory not found"
echo

echo "Checking /etc/nginx/sites-enabled/:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "Directory not found"
echo

echo "Checking /etc/nginx/conf.d/:"
ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "Directory not found"
echo

echo "6. Looking for your domain (flabs2fabs.omchat.ovh):"
for config_file in $(sudo find /etc/nginx -name "*.conf" -type f 2>/dev/null); do
    if sudo grep -q "flabs2fabs\|omchat" "$config_file"; then
        echo "Found in: $config_file"
        sudo grep -n "server_name\|listen\|root\|location\|proxy_pass" "$config_file" | grep -v "^#"
        echo "--- Content of $config_file ---"
        sudo cat "$config_file"
        echo "--- End of $config_file ---"
        echo
    fi
done

echo "7. Active Ports and Services:"
sudo netstat -tulpn | grep -E ":80|:443|:3000|:8000|:8080"
echo

echo "8. Check for Let's Encrypt SSL certificates:"
sudo ls -la /etc/letsencrypt/live/ 2>/dev/null || echo "No Let's Encrypt directory found"
sudo ls -la /etc/ssl/certs/ 2>/dev/null | grep -i "omchat\|flabs" || echo "No matching SSL certs found"
