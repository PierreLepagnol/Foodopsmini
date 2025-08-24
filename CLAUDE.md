# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FoodOps Pro is a realistic, educational restaurant management game in Python 3.11+. It simulates French business operations including menu engineering, inventory management (FEFO), French accounting (PCG), payroll with French labor law, and market competition.

## Common Development Commands

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_market_allocation.py -v
python -m pytest tests/test_ledger_vat.py -v
python -m pytest tests/test_payroll.py -v
python -m pytest tests/test_integration.py -v
```

### Code Quality
```bash
# Format code with Black
black src/ tests/ --line-length 88

# Lint with Ruff
ruff check src/ tests/

# Type checking with MyPy
mypy src/

# Install development dependencies
pip install -e ".[dev]"
```

### Game Execution
```bash
# Classic CLI version
python -m src.game_engine.cli
python -m src.game_engine.cli --scenario examples/scenarios/base.yaml

# Professional CLI with rich UI
python -m src.game_engine.cli_pro
python -m src.game_engine.cli_pro --scenario admin_configs/preset_demo.yaml

# Administrator mode for instructors
python -m src.game_engine.cli_pro --admin

# Quick launchers
python start_pro.py        # Full Pro version
python start_admin.py      # Admin configuration mode
python start_demo.py       # Quick 3-turn demo
```

## Architecture Overview

The codebase follows a domain-driven design pattern with clear separation of concerns:

### Core Game Engine
- **Market Engine** (`core/market.py`): Demand allocation algorithm with 3 market segments (Students 35%, Families 40%, Foodies 25%). Handles competition with AI restaurants and capacity constraints.
- **Costing Engine** (`core/costing.py`): Recipe cost calculation with realistic ingredient yields, waste percentages, and supplier pricing. Enhanced with labor cost calculation by restaurant type.
- **Procurement System** (`core/procurement.py`): Purchase order management with supplier catalogs, minimum order quantities, and pack sizing. Integrates with FEFO stock management.
- **Ledger System** (`core/ledger.py`): French accounting (PCG) with VAT management (5.5%, 10%, 20%), depreciation, and social charges.
- **Payroll System** (`core/payroll_fr.py`): French labor law compliance with social charges, overtime calculations, and contract types.

### Domain Models
- **Restaurant** (`domain/restaurant.py`): Core business entity with capacity, menu pricing, employee management, and financial state.
- **Commerce** (`domain/commerce.py`): Commercial property system for the Pro version - rent, traffic, competition analysis.
- **Competition** (`domain/competition.py`): AI competitor behavior with different difficulty levels and market positioning.
- **Scenario** (`domain/scenario.py`): Game configuration with market parameters, economic cycles, and victory conditions.
- **Stock Management** (`domain/stock.py`, `domain/stock_advanced.py`): FEFO inventory system with expiration tracking, supplier lot management.
- **Advanced Features** (`domain/achievements.py`, `domain/marketing.py`, `domain/finance_advanced.py`, `domain/random_events.py`): Achievement system, marketing campaigns, advanced financing options, and random events.

### Data Management
- **DataLoader** (`io/data_loader.py`): Handles CSV/JSON/YAML loading with validation. Supports both simple CSV files and complex YAML scenarios.
- **Persistence** (`io/persistence.py`): Game state save/load functionality for multi-session games.
- **Save Manager** (`io/save_manager.py`): Advanced save/load functionality with game state management.
- **Export** (`io/export.py`): Results export to JSON with comprehensive KPIs for educational analysis.

### User Interfaces
- **ConsoleUI** (`ui/console_ui.py`): Rich console interface for Pro version with progress bars, tables, and color formatting.
- **DecisionMenu** (`ui/decision_menu.py`): Interactive decision-making interface with comprehensive business management tools (menu pricing, HR, procurement, marketing, investments, financing, reports). Supports automation settings and line-by-line purchase confirmations.
- **Financial Reports** (`ui/financial_reports.py`): Comprehensive financial reporting with P&L statements, balance sheets, and KPI dashboards.
- **Tutorial System** (`ui/tutorial.py`): Interactive tutorial and help system for new players.
- **AdminConfig** (`admin/admin_config.py`): Comprehensive instructor configuration tool with session management, game parameters, automation controls, market settings, evaluation criteria, and restrictions management.

## Key Business Logic

### Market Allocation Algorithm
The market engine uses a sophisticated allocation system:
1. Each market segment has distinct preferences (price sensitivity, cuisine type preference)
2. Restaurants compete based on price positioning, capacity, and service quality
3. Demand is allocated proportionally with capacity constraints
4. Unserved customers become "lost sales" affecting reputation

### Commerce & Location Management
The Pro version includes a comprehensive commerce system:
- Multiple location types: city center, suburbs, commercial zones, student quarters
- Each location has unique characteristics (foot traffic, competition, rent, size)
- Purchase process includes acquisition cost, renovation needs, and lease terms
- Location affects customer base, operating costs, and market positioning

### French Accounting Integration
All financial transactions follow French accounting standards:
- Chart of accounts with proper debit/credit entries
- VAT collection and deduction with different rates per product category
- Social charges calculation with current French rates
- Automatic depreciation of equipment over regulatory periods

### Recipe Costing Precision
Cost calculation includes:
- Ingredient waste percentages during preparation
- Cooking yield losses (e.g., meat shrinkage)
- Supplier-specific pricing with minimum order quantities
- Dynamic pricing based on market conditions and seasonality
- Labor cost calculation varying by restaurant type (Fast: -15%, Classic: base, Brasserie: +10%, Gastronomique: +40%)

### Procurement & Inventory Management
The procurement system provides:
- Automatic demand forecasting based on recipe requirements and sales predictions
- Multi-supplier catalog support with pack sizing and MOQ handling
- Purchase order generation with line-by-line confirmation options
- FEFO (First Expired, First Out) inventory management
- Real-time stock tracking with expiration date monitoring

## Data Files Structure

### Static Data (CSV format)
- `src/foodops_pro/data/ingredients.csv`: 35+ ingredients with realistic pricing
- `src/foodops_pro/data/recipes.csv`: 20+ balanced recipes across segments
- `src/foodops_pro/data/recipe_items.csv`: Detailed recipe specifications with yields
- `src/foodops_pro/data/suppliers.csv`: 8 suppliers with different terms and specialties
- `src/foodops_pro/data/hr_tables.json`: French payroll tables with current rates

### Scenario Configuration (YAML)
- `examples/scenarios/base.yaml`: Default game parameters
- `admin_configs/preset_*.yaml`: Educational presets for different course levels
- Supports market sizing, AI difficulty, economic events, and victory conditions

## Testing Strategy

The test suite covers critical business logic:
- **Market allocation accuracy** under various competitive scenarios
- **French VAT calculations** with mixed product baskets
- **Payroll computations** with overtime and social charges
- **Recipe costing precision** with waste and yield factors
- **Integration tests** for complete game turns

When adding features, ensure tests cover both happy path and edge cases, especially for financial calculations which must be precise for educational credibility.

## Administrative Configuration System

The admin interface provides comprehensive control over game sessions:

### Session Management
- Course information (instructor name, course code, academic year)
- Game parameters (player limits, turn count, budget ranges)
- AI difficulty settings (easy, medium, hard) with configurable AI count

### Automation Controls
- Auto-forecast: Automatic demand prediction based on historical sales
- Auto-purchase: Intelligent purchase order suggestions based on stock levels
- Line confirmation: Require explicit approval for each purchase order line

### Market & Competition Settings
- Total market size configuration (100-2000 customers per turn)
- Market growth rate settings (-5% to +10% annually)
- Competition intensity levels (low, normal, high)
- Available commerce locations selection

### Educational Features
- Scoring system with weighted criteria: Survival (30%), Profitability (25%), Growth (20%), Efficiency (15%), Strategy (10%)
- Random events and seasonal effects toggles
- Economic cycle simulation controls
- Detailed feedback and hint systems

## Educational Considerations

This is primarily an educational tool for business/hospitality students. When making changes:
- Maintain realistic business parameters based on French market data
- Preserve the pedagogical balance between complexity and accessibility
- Ensure financial calculations remain accurate for teaching purposes
- Consider multi-language support for international education markets
- Validate that game mechanics reinforce intended learning objectives

The game supports various educational scenarios from simple 3-turn demos to complex 24-turn competitions with multiple AI difficulty levels.

## Development Notes

### Recent Enhancements
- Enhanced decision menu with comprehensive business management tools
- Procurement system with supplier catalogs and FEFO inventory management
- Administrative configuration system with granular control over game parameters
- Commerce acquisition phase for realistic property selection
- Labor cost calculation varying by restaurant type
- Advanced automation and confirmation controls for educational environments

### Integration Points
- The `DecisionMenu` class integrates with multiple systems and requires proper injection of suppliers catalog and admin settings
- The `cli_pro.py` handles both regular gameplay and administrative configuration modes
- The procurement system (`core/procurement.py`) works closely with stock management and supplier catalogs
- Financial calculations must maintain precision for educational credibility across all systems