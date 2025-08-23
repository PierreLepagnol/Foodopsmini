  Architecture & Design Philosophy

  foodops_pro/:
  - Domain-Driven Design: Clear separation between core business logic, domain models,
  and infrastructure
  - Educational Focus: Designed specifically for teaching with French business standards
   (PCG accounting, FEFO inventory)
  - Professional Scalability: Modular architecture supporting complex features like
  advanced finance, marketing campaigns, and achievement systems

  FoodOPS_V1/:
  - Prototype Architecture: More experimental, rapid-development approach
  - Pydantic-based Models: Heavy use of Pydantic for data validation and serialization
  - Simpler Structure: Less complex but more direct implementation

  Core Engine Differences

  Market Engine:
  - foodops_pro/: Sophisticated market allocation with 3 segments (Students 35%,
  Families 40%, Foodies 25%), seasonality effects, competition management, and
  reputation system
  - FoodOPS_V1/: Simpler customer allocation based on restaurant capacity and basic
  market segments

  Costing System:
  - foodops_pro/: Advanced recipe costing with waste percentages, yield calculations,
  FEFO stock management, and labor cost variations by restaurant type (-15% Fast, +40%
  Gastronomique)
  - FoodOPS_V1/: Basic costing with fixed margins per restaurant type (Fast: 2.5x,
  Bistro: 3.0x, Gastro: 3.8x)

  Financial System:
  - foodops_pro/: Full French accounting (PCG) with VAT management, depreciation, social
   charges, and advanced financing options
  - FoodOPS_V1/: Simplified accounting with basic ledger system, loan payments, and
  depreciation

  Domain Model Complexity

  Restaurant Management:
  - foodops_pro/: Advanced restaurant types with quality management, ingredient quality
  levels (1-5), reputation tracking, customer satisfaction history
  - FoodOPS_V1/: Basic restaurant classes (FastFood, Bistro, Gastro) with service speed
  differences and staff satisfaction tracking

  Inventory & Procurement:
  - foodops_pro/: Full FEFO inventory system, procurement planning with supplier
  catalogs, minimum order quantities, pack sizing
  - FoodOPS_V1/: Basic inventory management with finished product batches and simple
  stock tracking

  Employee Management:
  - foodops_pro/: Comprehensive HR system with French labor law compliance, contract
  types, social charges calculation
  - FoodOPS_V1/: Basic employee management with service/kitchen minutes allocation

  User Interface & Experience

  Decision Interface:
  - foodops_pro/: Rich console UI with comprehensive decision menu covering menu
  pricing, HR, procurement, marketing, investments, and financing
  - FoodOPS_V1/: Director's office interface with basic recipe management and staff
  decisions

  Admin Configuration:
  - foodops_pro/: Comprehensive admin system with session management, automation
  controls, market settings, and evaluation criteria
  - FoodOPS_V1/: Basic game initialization and configuration

  Educational Features

  Pedagogical Tools:
  - foodops_pro/: Built-in tutorial system, achievement tracking, detailed KPI
  dashboards, educational scenarios with different difficulty levels
  - FoodOPS_V1/: More direct gameplay experience with basic financial reporting

  Data Management:
  - foodops_pro/: Sophisticated data loading system supporting CSV/JSON/YAML with
  validation, comprehensive export for educational analysis
  - FoodOPS_V1/: JSON/CSV based data with Pydantic validation
