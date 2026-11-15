# Project Brief: IKEA TISKEN Japanese Minimalist Soap Drainer

- **Project ID**: `tisken-soap-drainer`
- **Target Hardware / Ecosystem**: IKEA TISKEN Corner Basket (suction-mounted shower/bath caddy)
- **Recommended Material**: Matte White / Warm-White PETG (bath humidity & soap resistant)
- **Current Version**: `v004` (*Hamon* Japanese Zen Ripple Edition)
- **Status**: `CAD Verified` (awaiting user physical test print)

## 1. Purpose & Requirements
- Hook-on round soap drainer for the front guard rail of an IKEA TISKEN corner basket.
- Minimalist Japanese aesthetic (*Muji / Yamazaki Home / Hamon* water-ripple motif).
- 100% hollow open bottom so water and suds drip straight through into the bathtub/shower below with zero pooling.
- Self-supporting flat FDM print (`Z = 0` build plate, zero supports).

## 2. Measured Dimensions & Protected Interfaces
| Interface | Measured Value | Design Clearance / Tolerance | Resulting CAD Dimension | Source |
| :--- | :--- | :--- | :--- | :--- |
| TISKEN Corner Basket Front Rail | `7.5 – 8.0 mm` | `+0.5 – 1.0 mm` slip fit | `8.5 mm` hook throat gap | User measurement |
| Soap Dish Outer Diameter | `Ø110 mm` | Round/oval soap bars up to ~95 mm | `Ø110.0 mm` outer (`Ø104.4 mm` inner) | User requirement |
| Standoff from Basket Front | — | Clear basket curvature | `6.0 mm` neck + lower bumper foot | Design spec |

## 3. Acceptance Criteria
- [x] Watertight manifold solid (`scripts/cad_check.py` passed)
- [x] Single connected component (`connected_components == 1`)
- [x] Support-free FDM print orientation verified
- [ ] Physical fit on TISKEN corner basket & bath drip confirmed by user
