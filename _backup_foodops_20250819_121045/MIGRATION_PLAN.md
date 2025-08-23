# FoodOps Pro: Complete Migration Plan to Next.js

## Executive Summary

This plan outlines the complete migration of FoodOps Pro from a Python console-based educational restaurant management game to a modern Next.js web application. The migration will preserve all educational value while significantly enhancing user experience, collaboration capabilities, and instructor tools.

## Current System Analysis

### Architecture Overview
- **Language**: Python 3.11+ with dataclasses and type hints
- **UI**: Console-based with rich formatting (ConsoleUI class)
- **Data**: CSV/JSON files + YAML scenarios
- **Dependencies**: PyYAML, Pandas, Pytest
- **Deployment**: Local Windows batch files + HTML launcher

### Core Business Components
1. **Domain Models**: 17 domain classes (Restaurant, Employee, Recipe, etc.)
2. **Core Engines**: Market allocation, Recipe costing, French accounting, Procurement
3. **Game Modes**: Classic CLI, Pro CLI with commerce acquisition, Admin configuration
4. **Educational Features**: Turn-based gameplay, realistic French business simulation
5. **Data Management**: FEFO inventory, supplier catalogs, scenario configuration

## Target Architecture: Next.js Web Application

### Technology Stack
- **Frontend**: Next.js 14+ with App Router, React 18, TypeScript
- **Styling**: Tailwind CSS + Headless UI + Framer Motion
- **Database**: PostgreSQL with Prisma ORM
- **API**: tRPC for end-to-end type safety
- **Authentication**: NextAuth.js with role-based access
- **Real-time**: WebSockets for multiplayer synchronization
- **Charts**: Recharts for financial visualization
- **Testing**: Jest + React Testing Library + Playwright
- **Deployment**: Vercel with PostgreSQL

## Phase 1: Foundation & Core Migration (4 weeks)

### Week 1: Project Setup & Database Design
```
foodops-web/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Authentication routes
│   │   ├── admin/             # Admin dashboard
│   │   ├── game/              # Game interface
│   │   └── api/               # API routes
│   ├── components/            # React components
│   │   ├── ui/                # Base UI components
│   │   ├── game/              # Game-specific components
│   │   └── admin/             # Admin components
│   ├── lib/                   # Business logic
│   │   ├── game/              # Game engines
│   │   ├── accounting/        # French accounting
│   │   └── utils/             # Utilities
│   ├── types/                 # TypeScript types
│   └── hooks/                 # React hooks
├── prisma/                    # Database schema
├── public/                    # Static assets
└── tests/                     # Test files
```

**Database Schema Migration**:
```sql
-- Core game entities
restaurants, ingredients, recipes, recipe_items
suppliers, employees, stock_lots
scenarios, market_segments

-- Game session management
game_sessions, session_participants
turns, turn_decisions, market_results

-- Educational features
admin_configs, instructor_profiles
student_progress, achievements

-- Real-time multiplayer
game_states, player_actions
commerce_locations, available_properties
```

### Week 2: Type System & Domain Models
**TypeScript Interface Generation**:
- Convert Python dataclasses to TypeScript interfaces
- Zod schemas for runtime validation
- Prisma client type generation
- tRPC router type safety

**Example Migration**:
```python
# Python
@dataclass
class Restaurant:
    id: str
    name: str
    type: RestaurantType
    capacity_base: int
    cash: Decimal
```

```typescript
// TypeScript + Zod
export const RestaurantSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.nativeEnum(RestaurantType),
  capacityBase: z.number().int().positive(),
  cash: z.number().multipleOf(0.01)
})
export type Restaurant = z.infer<typeof RestaurantSchema>
```

### Week 3: Business Logic Migration
**Core Engine Ports**:
1. **Market Engine**: Python → TypeScript with same allocation algorithms
2. **Recipe Costing**: Decimal precision preservation for educational accuracy
3. **French Accounting**: PCG compliance with VAT calculations
4. **Procurement System**: FEFO inventory + supplier catalog management

**Performance Considerations**:
- Server-side calculations for game logic integrity
- Client-side optimistic updates for UI responsiveness
- Background jobs for complex financial calculations

### Week 4: API Layer & Authentication
**tRPC Router Structure**:
```typescript
export const appRouter = t.router({
  auth: authRouter,
  game: gameRouter,        // Game state & actions
  admin: adminRouter,      // Instructor tools
  market: marketRouter,    // Market simulation
  finance: financeRouter,  // Accounting & reports
})
```

**Authentication & Authorization**:
- Role-based access: Student, Instructor, Admin
- Game session permissions
- Multi-tenant support for educational institutions

## Phase 2: Game Interface Development (6 weeks)

### Week 5-6: Core Game Flow
**Game States & Navigation**:
1. **Lobby**: Session creation, player joining
2. **Commerce Selection**: Property acquisition interface
3. **Restaurant Setup**: Naming, initial configuration
4. **Turn-based Gameplay**: Decision making cycles
5. **Results & Analysis**: Performance reporting

**Component Architecture**:
```tsx
// Game session wrapper
<GameSessionProvider>
  <GameHeader />
  <GameSidebar />
  <GameContent>
    {phase === 'commerce' && <CommerceSelection />}
    {phase === 'setup' && <RestaurantSetup />}
    {phase === 'decisions' && <DecisionInterface />}
    {phase === 'results' && <TurnResults />}
  </GameContent>
</GameSessionProvider>
```

### Week 7-8: Decision Management Interface
**Interactive Business Tools**:
1. **Menu Engineering**: Drag-drop recipe management, pricing calculator
2. **HR Management**: Employee hiring, scheduling, payroll preview
3. **Procurement Dashboard**: Inventory levels, purchase orders, supplier comparison
4. **Marketing Builder**: Campaign creation with budget allocation
5. **Financial Center**: Cash flow monitoring, loan management

**Advanced UI Components**:
- Data tables with sorting/filtering for large datasets
- Chart visualizations for KPIs and trends
- Modal workflows for complex operations
- Real-time validation and error handling

### Week 9-10: Real-time Multiplayer
**WebSocket Implementation**:
- Turn synchronization across all players
- Live competitor actions visibility
- Real-time market updates
- Turn countdown timers
- Spectator mode for instructors

**State Management**:
```typescript
// Zustand store for game state
interface GameStore {
  session: GameSession | null
  currentTurn: number
  players: Player[]
  marketResults: MarketResult[]
  // Real-time sync methods
  syncTurnDecisions: () => void
  updateMarketState: (data: MarketUpdate) => void
}
```

## Phase 3: Advanced Features & Educational Tools (4 weeks)

### Week 11-12: Data Visualization & Analytics
**Financial Reporting Suite**:
- Interactive P&L statements with drill-down capabilities
- Balance sheet visualization with account breakdowns
- Cash flow charts with forecast projections
- KPI dashboards with industry benchmarks

**Performance Analytics**:
- Student progress tracking over multiple sessions
- Comparative analysis between teams
- Decision impact visualization
- Learning outcome measurement

### Week 13-14: Educational Enhancement
**Tutorial System**:
- Interactive onboarding with step-by-step guidance
- Context-sensitive help during gameplay
- Video tutorials embedded in interface
- Glossary of business terms

**Achievement System**:
- Milestone tracking (first profit, market leadership, etc.)
- Badges for educational objectives
- Progress portfolios for students
- Instructor assessment tools

## Phase 4: Admin Dashboard & Instructor Tools (3 weeks)

### Week 15: Admin Interface
**Session Management**:
- Course creation and configuration
- Student enrollment and team formation
- Game parameter customization
- Real-time session monitoring

**Educational Controls**:
- Scenario builder with visual editor
- Market condition presets
- Automated assessment configuration
- Export tools for gradebooks

### Week 16: Advanced Configuration
**Automation Features**:
- Auto-forecast toggle for demand prediction
- Purchase order suggestion system
- Line-by-line confirmation controls
- Custom business rules engine

**Analytics Dashboard**:
- Class performance overview
- Individual student analytics
- Engagement metrics
- Learning objective tracking

### Week 17: Testing & Polish
**Comprehensive Testing**:
- Unit tests for business logic accuracy
- Integration tests for multiplayer scenarios
- E2E tests for complete user journeys
- Performance testing under load

## Phase 5: Deployment & Launch (2 weeks)

### Week 18: Production Deployment
**Infrastructure Setup**:
- Vercel deployment with PostgreSQL
- CDN configuration for static assets
- WebSocket scaling considerations
- Monitoring and alerting

**Security & Performance**:
- Data encryption and privacy compliance
- Rate limiting and abuse prevention
- Performance optimization
- Backup and disaster recovery

### Week 19: Launch & Documentation
**Go-Live Preparation**:
- User documentation and training materials
- Instructor onboarding guide
- Technical documentation
- Support system setup

## Migration Benefits & Value Propositions

### For Students
- **Accessibility**: Play from any device with internet
- **Collaboration**: Real-time multiplayer with classmates
- **Engagement**: Modern, intuitive interface with gamification
- **Learning**: Enhanced visualizations and immediate feedback

### For Instructors
- **Control**: Comprehensive admin tools and configuration options
- **Monitoring**: Real-time student progress tracking
- **Assessment**: Automated grading and detailed analytics
- **Flexibility**: Custom scenarios and market conditions

### For Institutions
- **Scalability**: Cloud-native architecture supports large classes
- **Maintenance**: Reduced IT overhead with SaaS deployment
- **Integration**: API support for LMS integration
- **Analytics**: Institution-wide usage and outcome tracking

## Technical Considerations

### Performance Requirements
- **Concurrent Users**: Support 100+ students per session
- **Real-time Updates**: <100ms latency for game actions
- **Data Accuracy**: Preserve financial calculation precision
- **Uptime**: 99.9% availability during academic terms

### Security & Privacy
- **Data Protection**: GDPR/FERPA compliance for educational data
- **Authentication**: SSO integration with institutional systems
- **Access Control**: Granular permissions and audit trails
- **Content Security**: XSS protection and input validation

### Localization & Accessibility
- **Internationalization**: Multi-language support framework
- **Accessibility**: WCAG 2.1 AA compliance
- **Mobile Responsiveness**: Tablet and phone optimization
- **Offline Capability**: Progressive Web App features

## Risk Mitigation

### Technical Risks
- **Complexity**: Phased delivery with MVP validation
- **Performance**: Load testing and optimization cycles
- **Data Migration**: Automated scripts with rollback procedures
- **Browser Compatibility**: Cross-browser testing matrix

### Educational Risks
- **Learning Curve**: Comprehensive training and documentation
- **Feature Parity**: Systematic migration checklist
- **Adoption**: Pilot programs with early adopters
- **Feedback Loop**: Continuous user research and iteration

## Success Metrics

### Technical KPIs
- Page load times <2 seconds
- Game action response times <100ms
- 99.9% uptime during peak usage
- Zero data loss incidents

### Educational KPIs
- 90%+ instructor satisfaction scores
- 85%+ student engagement rates
- 50% reduction in setup time vs. Python version
- 25% improvement in learning outcome assessments

## Detailed Component Migration Map

### Domain Models Migration
| Python Module | TypeScript Equivalent | Notes |
|---------------|----------------------|-------|
| `domain/restaurant.py` | `types/restaurant.ts` | Preserve capacity calculations |
| `domain/employee.py` | `types/employee.ts` | French labor law compliance |
| `domain/recipe.py` | `types/recipe.ts` | Waste/yield calculations |
| `domain/ingredient.py` | `types/ingredient.ts` | VAT rate management |
| `domain/stock.py` | `types/stock.ts` | FEFO logic preservation |
| `domain/scenario.py` | `types/scenario.ts` | Market segment definitions |
| `domain/commerce.py` | `types/commerce.ts` | Property acquisition system |

### Core Engine Migration
| Python Module | TypeScript Equivalent | Critical Features |
|---------------|----------------------|-------------------|
| `core/market.py` | `lib/game/market.ts` | Allocation algorithm accuracy |
| `core/costing.py` | `lib/game/costing.ts` | Decimal precision for education |
| `core/ledger.py` | `lib/accounting/ledger.ts` | French PCG compliance |
| `core/payroll_fr.py` | `lib/accounting/payroll.ts` | Social charges calculation |
| `core/procurement.py` | `lib/game/procurement.ts` | Multi-supplier catalog |

### UI Component Mapping
| Python UI Element | React Component | Enhancement |
|-------------------|-----------------|-------------|
| `ConsoleUI.print_box()` | `<Card />` | Rich styling with Tailwind |
| `DecisionMenu` | `<GameInterface />` | Interactive forms with validation |
| `FinancialReports` | `<ReportsManager />` | Charts and drill-down capabilities |
| `AdminConfig` | `<AdminDashboard />` | Visual configuration builders |
| Progress bars | `<ProgressIndicator />` | Real-time updates with WebSockets |

## Database Schema Design

### Core Tables
```sql
-- Game management
CREATE TABLE game_sessions (
  id UUID PRIMARY KEY,
  instructor_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  scenario_id UUID REFERENCES scenarios(id),
  status VARCHAR(50) DEFAULT 'waiting',
  current_turn INTEGER DEFAULT 0,
  max_turns INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  ended_at TIMESTAMP
);

-- Player management
CREATE TABLE restaurants (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES game_sessions(id),
  owner_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  type restaurant_type NOT NULL,
  capacity_base INTEGER NOT NULL,
  speed_service DECIMAL(5,2) NOT NULL,
  cash DECIMAL(12,2) DEFAULT 0,
  equipment_value DECIMAL(12,2) DEFAULT 0,
  rent_monthly DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Turn-based gameplay
CREATE TABLE turns (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES game_sessions(id),
  turn_number INTEGER NOT NULL,
  phase VARCHAR(50) DEFAULT 'decisions',
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  UNIQUE(session_id, turn_number)
);

-- Decision tracking
CREATE TABLE player_decisions (
  id UUID PRIMARY KEY,
  turn_id UUID REFERENCES turns(id),
  restaurant_id UUID REFERENCES restaurants(id),
  decision_type VARCHAR(100) NOT NULL,
  decision_data JSONB NOT NULL,
  submitted_at TIMESTAMP DEFAULT NOW()
);

-- Market results
CREATE TABLE market_results (
  id UUID PRIMARY KEY,
  turn_id UUID REFERENCES turns(id),
  restaurant_id UUID REFERENCES restaurants(id),
  allocated_demand INTEGER NOT NULL,
  served_customers INTEGER NOT NULL,
  capacity INTEGER NOT NULL,
  utilization_rate DECIMAL(5,4) NOT NULL,
  revenue DECIMAL(12,2) NOT NULL,
  average_ticket DECIMAL(8,2) NOT NULL
);
```

### Static Data Tables
```sql
-- Game content
CREATE TABLE ingredients (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  unit VARCHAR(20) NOT NULL,
  cost_ht DECIMAL(8,2) NOT NULL,
  vat_rate DECIMAL(5,4) NOT NULL,
  shelf_life_days INTEGER NOT NULL,
  category VARCHAR(50) NOT NULL,
  density DECIMAL(6,4)
);

CREATE TABLE recipes (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  cuisine_type VARCHAR(50) NOT NULL,
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
  portions INTEGER NOT NULL,
  temps_prep_min INTEGER NOT NULL,
  temps_cuisson_min INTEGER NOT NULL
);

CREATE TABLE recipe_items (
  id UUID PRIMARY KEY,
  recipe_id VARCHAR(50) REFERENCES recipes(id),
  ingredient_id VARCHAR(50) REFERENCES ingredients(id),
  qty_brute DECIMAL(8,3) NOT NULL,
  perte_prep DECIMAL(5,4) DEFAULT 0,
  perte_cuisson DECIMAL(5,4) DEFAULT 0
);
```

This comprehensive migration plan transforms FoodOps Pro from a local Python application into a modern, scalable web-based educational platform while preserving all its educational value and business simulation accuracy.