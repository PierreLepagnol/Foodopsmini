# Architecture

This document lists the active modules of FoodOps Pro and their roles.

## CLI Entry Points
- `src/foodops_pro/cli.py`: classic command line interface for the game.
- `src/foodops_pro/cli_pro.py`: enriched interface with pro features and admin mode.

## Admin Module
- `src/foodops_pro/admin/admin_config.py`: helpers and presets for instructors.

## Core Logic
- `src/foodops_pro/core/market.py`: market allocation and competition engine.
- `src/foodops_pro/core/costing.py`: recipe cost and margin calculations.
- `src/foodops_pro/core/ledger.py`: accounting with VAT utilities.
- `src/foodops_pro/core/payroll.py`: payroll computation with social charges.

## Domain Models
- `src/foodops_pro/domain/restaurant.py`: restaurant entities and operations.
- `src/foodops_pro/domain/recipe.py`: recipes and their ingredients.
- `src/foodops_pro/domain/ingredient.py`: ingredient definitions.
- `src/foodops_pro/domain/employee.py`: employee positions and contracts.
- `src/foodops_pro/domain/stock.py`: basic stock management.
- `src/foodops_pro/domain/stock_advanced.py`: advanced stock and waste tracking.
- `src/foodops_pro/domain/commerce.py`: business locations and acquisition.
- `src/foodops_pro/domain/marketing.py`: marketing campaigns and reviews.
- `src/foodops_pro/domain/finance_advanced.py`: advanced financial reporting.
- `src/foodops_pro/domain/scenario.py`: scenario configuration structures.

## I/O Utilities
- `src/foodops_pro/io/data_loader.py`: load CSV/JSON/YAML resources.
- `src/foodops_pro/io/persistence.py`: save and restore game state.
- `src/foodops_pro/io/export.py`: export KPIs and results.
- `src/foodops_pro/io/save_manager.py`: manage saved games.

## User Interface
- `src/foodops_pro/ui/console_ui.py`: console interactions.
- `src/foodops_pro/ui/decision_menu.py`: in-game menu navigation.
- `src/foodops_pro/ui/financial_reports.py`: financial report rendering.

## Scripts
- `scripts/find_unused.py`: scan imports to detect orphan modules.

