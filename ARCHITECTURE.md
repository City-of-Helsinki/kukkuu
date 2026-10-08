<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Kukkuu Platform Architecture](#kukkuu-platform-architecture)
  - [System Overview](#system-overview)
  - [Domain Concepts](#domain-concepts)
  - [Repository Landscape](#repository-landscape)
    - [1. Backend (`kukkuu`)](#1-backend-kukkuu)
    - [2. Public UI (`kukkuu-ui`)](#2-public-ui-kukkuu-ui)
    - [3. Admin UI (`kukkuu-admin`)](#3-admin-ui-kukkuu-admin)
    - [4. External Services & Shared Libraries](#4-external-services--shared-libraries)
  - [Data Flow Summary](#data-flow-summary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Kukkuu Platform Architecture

## System Overview
The Kukkuu ecosystem is a platform designed to facilitate the booking of cultural events for children (godchildren) by their guardians. It consists of a centralized backend and two distinct user interfaces tailored for different user groups (public users vs. administrative/organizer users).

For the full list of services and environment URLs, see the [Service architecture section in the README](README.md#service-architecture).

## Domain Concepts
- **Year Projects:** A core organizational unit. A child belongs to a year project based on their birth year. Events are also linked to specific year projects.
- **Ticketing:** Events can use internal ticketing (managed within Kukkuu) or external ticketing systems (like Ticketmaster, Lippu.fi, or Tixly) which may involve coupon codes.
- **Project-Scoped Admin Access:** Administrative privileges and roles can be scoped to specific year projects, allowing event organizers to manage only the events relevant to them.

## Repository Landscape

### 1. Backend (`kukkuu`)
*The anchor of the system.*
- **Role:** Core backend application, database owner, and primary API provider.
- **Tech Stack:** Django, GraphQL, PostgreSQL.
- **API Surfaces:**
  - **GraphQL API:** The primary API consumed exclusively by `kukkuu-ui` and `kukkuu-admin`.
  - **REST Report API (DRF):** A separate REST API under `/reports/` for data reporting.
  - **GDPR API:** Handles GDPR-related requests.
- **Authentication:** Keycloak integrated with Helsinki-Profile (Tunnistamo is legacy).
- **Other:** Includes standard Django Admin interfaces used directly by developers and the product owner for low-level system management.

### 2. Public UI (`kukkuu-ui`)
- **Role:** The public-facing web application.
- **Target Audience:** Guardians and custodians of godchildren.
- **Key Features:**
  - Allows guardians to browse available cultural events and register children as participants.
  - Consumes the `kukkuu` GraphQL API for transactional data (bookings, user profiles).
  - **CMS Integration:** Integrates deeply with the Headless CMS (WordPress) using the `react-helsinki-headless-cms` library to serve a large portion of its dynamic, informational content.

### 3. Admin UI (`kukkuu-admin`)
- **Role:** The administrative and event management dashboard.
- **Target Audience & Authentication:**
  - **Event Organizers:** External users (e.g., from private companies) who manage their events. They authenticate using the **Helsinki Profile**.
  - **System Administrators & Product Owners:** Internal city staff who manage the platform. They authenticate using the **City's AD credentials**.
- **Key Features:**
  - Consumes the `kukkuu` GraphQL API to manage events, view registrations, and administer the system.

### 4. External Services & Shared Libraries
- **Headless CMS (WordPress):** Provides dynamic page content for the public UI.
- **Notification Service API & Mailer:** Used by the backend to send SMS and email notifications to users.
- **CMS Library (`react-helsinki-headless-cms`):** A shared integration library used by the public UI to communicate with the Headless CMS. It is used by multiple projects outside of the Kukkuu ecosystem and is not modified here.

## Data Flow Summary
1. **Public Browsing:** `kukkuu-ui` fetches dynamic page content from WordPress via `react-helsinki-headless-cms` and transactional event availability from `kukkuu` (GraphQL).
2. **Registration:** Guardians submit bookings via `kukkuu-ui`, which mutate data in the `kukkuu` backend. The backend may trigger the Notification Service API / Mailer.
3. **Event Management:** Organizers log into `kukkuu-admin` (via Helsinki Profile) to create and manage the events that appear in the backend database.
4. **Platform Administration:** City staff log into `kukkuu-admin` (via AD) or the Django Admin in `kukkuu` to oversee operations.
