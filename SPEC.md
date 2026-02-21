# SPEC.md - Render Deployment Setup

## 1. Overview
This specification details the configuration required to deploy both the `velos-backend` and `velos-frontend` automatically using Render's Infrastructure as Code (`render.yaml`).

## 2. Requirements
- The backend must be deployed as a Docker Web Service using `backend/Dockerfile`.
- The frontend must be deployed as a Docker Web Service using `Dockerfile.frontend`.
- The frontend needs the backend API URL injected at build-time.
- The `render.yaml` must orchestrate both automated deployments from a single GitHub push.

## 3. Implementation Plan
- Update `Dockerfile.frontend` to declare `ARG VITE_API_BASE` and `ENV VITE_API_BASE=$VITE_API_BASE` before the Vite build step.
- Update `render.yaml` to define the `velos-frontend` service and set `VITE_API_BASE` to the generated backend URL.
- Output instructions for the user to push to GitHub and deploy via Render's "Blueprint" feature.
