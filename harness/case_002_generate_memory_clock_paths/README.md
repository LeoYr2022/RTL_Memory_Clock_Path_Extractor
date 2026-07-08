# case_002_generate_memory_clock_paths

## Purpose

This harness captures the four-SRAM clock-path sample rewritten with a `generate for` block. All generated memories share the `clk_pll` and `clk_osc` source clocks while using indexed internal arrays and generated memory clock path instances.

## Covered RTL Features

- `genvar` declaration
- Named `generate for` block
- Generated module instantiation
- Indexed wire arrays for memory clock and data connections
- Parameter expression using the generate index
- Memory-like module with `CLK` clock pin

## Golden Source

`expected/expected_clock_paths.json` is manually reviewed from `rtl/four_memory_clock_paths_generate.sv`.

The golden result tracks the clock path for each generated `simple_sram` instance:

- `gen_mem[0].u_mem`: `clk_pll` or `clk_osc` to `gen_mem[0].u_mem.CLK`
- `gen_mem[1].u_mem`: `clk_pll` or `clk_osc` to `gen_mem[1].u_mem.CLK`
- `gen_mem[2].u_mem`: `clk_pll` or `clk_osc` to `gen_mem[2].u_mem.CLK`
- `gen_mem[3].u_mem`: `clk_pll` or `clk_osc` to `gen_mem[3].u_mem.CLK`

## Regression

Regenerate the Draw.io diagram from the golden JSON:

```bash
python scripts/json_clock_paths_to_drawio.py --input harness/case_002_generate_memory_clock_paths/expected/expected_clock_paths.json --output harness/case_002_generate_memory_clock_paths/expected/generate_memory_clock_paths.drawio
```
