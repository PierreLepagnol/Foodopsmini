  Domain Distribution Analysis

  🏪 Restaurant Domain

  Functions that should belong to Restaurant class:

  1. _apply_player_decisions(restaurant: Restaurant, decisions: Dict) -
  Lines 390-417
    - Reason: Only operates on restaurant object, modifying prices,
  employees, and cash
    - Dependencies: Pure restaurant state manipulation
  2. _add_base_employees(restaurant: Restaurant, restaurant_type:
  RestaurantType) - Lines 246-283
    - Reason: Creates and adds employees to a specific restaurant
    - Dependencies: Only restaurant object and HR data
  3. _setup_base_menu(restaurant: Restaurant, restaurant_type:
  RestaurantType) - Lines 285-318
    - Reason: Configures menu items and prices for a specific restaurant
    - Dependencies: Only restaurant object and recipes data
  4. _get_speed_for_type(restaurant_type: RestaurantType) - Lines
  236-244
    - Reason: Pure calculation based on restaurant type
    - Dependencies: Static configuration data only

  🤖 AI/Competition Domain

  Functions that should belong to AI competitor management:

  1. _ai_decisions() - Lines 418-432
    - Reason: Implements AI decision logic for competitors
    - Dependencies: AI difficulty settings and competitor state
  2. _create_ai_competitors() - Lines 330-357
    - Reason: Creates and configures AI competitors
    - Dependencies: Commerce system and restaurant creation

  🏢 Commerce Domain

  Functions that should belong to Commerce/Property management:

  1. _select_commerce_for_player(player_num: int) - Lines 147-201
    - Reason: Handles commerce selection and purchase process
    - Dependencies: Commerce catalog, budget validation, UI
  2. _create_restaurant_from_commerce(location, budget, player_num) -
  Lines 203-234
    - Reason: Transforms a commerce location into an operational
  restaurant
    - Dependencies: Commerce location, restaurant creation

  🎮 Game Engine/Simulation Domain

  Functions that should belong to Game Engine:

  1. _update_restaurants(results: Dict) - Lines 482-510
    - Reason: Updates all restaurants based on market simulation results
    - Dependencies: Market results, financial calculations
  2. _game_loop() - Lines 359-389
    - Reason: Core game simulation loop
    - Dependencies: Decision processing, AI, market engine, results
  display

  📊 Reporting/UI Domain

  Functions that should belong to UI/Reporting system:

  1. _display_turn_results(results: Dict, turn: int) - Lines 433-481
    - Reason: Pure presentation logic for turn results
    - Dependencies: Only UI functions and data formatting
  2. _export_results() - Lines 544-567
    - Reason: Results export functionality
    - Dependencies: Export system and file I/O

  🎯 Game Session/Orchestration Domain

  Functions that should remain in CLI orchestrator:

  1. start_game() - Lines 98-116
    - Reason: Main game flow orchestration
    - Dependencies: All game phases
  2. _commerce_selection_phase() - Lines 118-146
    - Reason: Commerce acquisition phase orchestration
    - Dependencies: Player setup and commerce selection
  3. _setup_players() - Lines 320-328
    - Reason: Player validation and setup coordination
    - Dependencies: Player state validation
  4. _end_game() - Lines 511-543
    - Reason: End game sequence orchestration
    - Dependencies: Ranking, results display, export
  5. load_settings() - Lines 92-96
    - Reason: Configuration management for game session
    - Dependencies: Configuration files
  6. main() - Lines 569-586
    - Reason: Application entry point
    - Dependencies: Game initialization

  Refactoring Recommendations

  High Priority Moves

  1. Restaurant Domain Extensions:
    - Move _apply_player_decisions → Restaurant.apply_decisions()
    - Move _add_base_employees → Restaurant.setup_base_employees()
    - Move _setup_base_menu → Restaurant.setup_base_menu()
    - Move _get_speed_for_type → RestaurantType.get_service_speed()
  (static method)

  Medium Priority Moves

  2. AI Domain Creation:
    - Create AICompetitorManager class
    - Move _ai_decisions → AICompetitorManager.make_decisions()
    - Move _create_ai_competitors →
  AICompetitorManager.create_competitors()
  3. Commerce Domain Extensions:
    - Move _select_commerce_for_player →
  CommerceManager.player_selection_flow()
    - Move _create_restaurant_from_commerce →
  CommerceLocation.create_restaurant()

  Low Priority Moves

  4. Engine/Reporting Separation:
    - Move _update_restaurants → GameEngine.update_restaurants_state()
    - Move _display_turn_results →
  ResultsRenderer.display_turn_results()
    - Move _export_results → ResultsExporter.export_game_results()

  Benefits of This Distribution

  1. Single Responsibility: Each domain handles its specific concerns
  2. Testability: Domain methods can be unit tested in isolation
  3. Reusability: Restaurant operations can be reused across different
  UIs
  4. Maintainability: Changes to business logic are contained within
  domains
  5. Separation of Concerns: UI/orchestration separate from business
  logic

  The CLI would become a thin orchestration layer that coordinates
  between domains, making the codebase more modular and maintainable.