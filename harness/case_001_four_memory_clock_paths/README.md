# case_001_four_memory_clock_paths

## Purpose

This harness captures a top-level RTL sample with four SRAM instances. Each memory clock is driven through a mux, divider, and bypass block.

## Covered RTL Features

- Multiple module definitions in one SystemVerilog file
- Parameterized module instantiation
- Named port connections
- Vector bit-select control signals
- Memory-like module with `CLK` clock pin
- Clock mux, divider, and bypass connectivity

## Golden Source

`expected/expected_clock_paths.json` is manually reviewed from `rtl/four_memory_clock_paths.sv`.

The golden result tracks the clock path for each `simple_sram` instance:

- `u_mem0`: `clk_pll0` or `clk_osc0` to `u_mem0.CLK`
- `u_mem1`: `clk_pll1` or `clk_osc1` to `u_mem1.CLK`
- `u_mem2`: `clk_test0` or `clk_scan0` to `u_mem2.CLK`
- `u_mem3`: `clk_test1` or `clk_scan1` to `u_mem3.CLK`

## Regression

Regenerate the Draw.io diagram from the golden JSON:

```bash
python scripts/json_clock_paths_to_drawio.py --input harness/case_001_four_memory_clock_paths/expected/expected_clock_paths.json --output harness/case_001_four_memory_clock_paths/expected/four_memory_clock_paths.drawio
```
