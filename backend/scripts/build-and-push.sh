#!/bin/bash
# Script para build local + push para Docker Hub
# Uso: ./scripts/build-and-push.sh [IMAGE_NAME] [VERSION]

set -e

# Configurações
IMAGE_NAME="${1:-seu-usuario/cosmoastrologia}"
VERSION="${2:-latest}"
FULL_IMAGE="$IMAGE_NAME:$VERSION"

echo "🔨 Building image: $FULL_IMAGE"
echo ""

# Build
cd "$(dirname "$0")/.."
docker build -t "$FULL_IMAGE" -f Dockerfile.build-local .

echo ""
echo "📤 Pushing to Docker Hub..."
docker push "$FULL_IMAGE"

echo ""
echo "✅ Done! Image: $FULL_IMAGE"
echo ""
echo "📋 Próximos passos:"
echo "1. No Railway, configure:"
echo "   - Settings → Deploy → Deploy from Docker Hub"
echo "   - Image: $FULL_IMAGE"
echo "2. Railway vai baixar a imagem (não fazer build)"

