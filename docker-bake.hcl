# Image variants of the app (see tasks.md, Phase 4).
# Build both:  docker buildx bake
# Build one:   docker buildx bake prod

group "default" {
  targets = ["dev", "prod"]
}

# Shared settings, inherited by both variants.
target "_common" {
  context    = "."
  dockerfile = "Dockerfile"
}

# debian:trixie-slim, with shell and apt.
target "dev" {
  inherits = ["_common"]
  target   = "dev"
  tags     = ["ai-server:dev"]
}

# distroless cc-debian13, without shell and package manager.
target "prod" {
  inherits = ["_common"]
  target   = "prod"
  tags     = ["ai-server:prod"]
}
