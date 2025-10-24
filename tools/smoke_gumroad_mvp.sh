#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
export MARIA_HOME="$PWD"

echo "1) mining ideas"
python3 tools/earn_gumroad/idea_miner.py >/dev/null

echo "2) building 3 products"
python3 tools/earn_gumroad/product_builder.py >/dev/null

echo "3) packaging"
python3 tools/earn_gumroad/package_product.py >/dev/null

echo "4) verifying"
count_dirs=$(find artifacts/gumroad -maxdepth 1 -type d -not -path '*/\.*' | wc -l | awk '{print $1}')
count_listings=$(ls artifacts/gumroad/*/listing.json 2>/dev/null | wc -l | awk '{print $1}')
count_zips=$(ls artifacts/gumroad/*/assets.zip 2>/dev/null | wc -l | awk '{print $1}')
# відняти кореневий каталог із count_dirs
count_dirs=$((count_dirs-1))
echo "dirs=$count_dirs listings=$count_listings zips=$count_zips"
