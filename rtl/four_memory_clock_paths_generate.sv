module clk_mux2 (
    input  wire clk_a,
    input  wire clk_b,
    input  wire sel,
    output wire clk_out
);
    assign clk_out = sel ? clk_b : clk_a;
endmodule

module clk_bypass (
    input  wire clk_main,
    input  wire clk_bypass,
    input  wire bypass_en,
    output wire clk_out
);
    assign clk_out = bypass_en ? clk_bypass : clk_main;
endmodule

module clk_divider #(
    parameter integer DIVIDE_BY = 2
) (
    input  wire clk_in,
    input  wire rst_n,
    output reg  clk_out
);
    reg [7:0] div_cnt;

    always @(posedge clk_in or negedge rst_n) begin
        if (!rst_n) begin
            div_cnt <= 8'd0;
            clk_out <= 1'b0;
        end else if (div_cnt == (DIVIDE_BY - 1)) begin
            div_cnt <= 8'd0;
            clk_out <= ~clk_out;
        end else begin
            div_cnt <= div_cnt + 8'd1;
        end
    end
endmodule

module simple_sram #(
    parameter integer ADDR_WIDTH = 8,
    parameter integer DATA_WIDTH = 32,
    parameter integer DEPTH = 256
) (
    input  wire                  CLK,
    input  wire                  CEN,
    input  wire                  WEN,
    input  wire [ADDR_WIDTH-1:0] A,
    input  wire [DATA_WIDTH-1:0] D,
    output reg  [DATA_WIDTH-1:0] Q
);
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    always @(posedge CLK) begin
        if (!CEN) begin
            if (!WEN) begin
                mem[A] <= D;
            end
            Q <= mem[A];
        end
    end
endmodule

module top (
    input  wire        rst_n,
    input  wire        clk_pll,
    input  wire        clk_osc,
    input  wire [3:0]  clk_mux_sel,
    input  wire [3:0]  clk_bypass_en,
    input  wire [3:0]  mem_cen,
    input  wire [3:0]  mem_wen,
    input  wire [7:0]  mem0_addr,
    input  wire [7:0]  mem1_addr,
    input  wire [7:0]  mem2_addr,
    input  wire [7:0]  mem3_addr,
    input  wire [31:0] mem0_wdata,
    input  wire [31:0] mem1_wdata,
    input  wire [31:0] mem2_wdata,
    input  wire [31:0] mem3_wdata,
    output wire [31:0] mem0_rdata,
    output wire [31:0] mem1_rdata,
    output wire [31:0] mem2_rdata,
    output wire [31:0] mem3_rdata
);
    localparam integer NUM_MEM = 4;

    wire [NUM_MEM-1:0] mem_mux_clk;
    wire [NUM_MEM-1:0] mem_div_clk;
    wire [NUM_MEM-1:0] mem_clk;

    wire [7:0]  mem_addr  [0:NUM_MEM-1];
    wire [31:0] mem_wdata [0:NUM_MEM-1];
    wire [31:0] mem_rdata [0:NUM_MEM-1];

    assign mem_addr[0] = mem0_addr;
    assign mem_addr[1] = mem1_addr;
    assign mem_addr[2] = mem2_addr;
    assign mem_addr[3] = mem3_addr;

    assign mem_wdata[0] = mem0_wdata;
    assign mem_wdata[1] = mem1_wdata;
    assign mem_wdata[2] = mem2_wdata;
    assign mem_wdata[3] = mem3_wdata;

    assign mem0_rdata = mem_rdata[0];
    assign mem1_rdata = mem_rdata[1];
    assign mem2_rdata = mem_rdata[2];
    assign mem3_rdata = mem_rdata[3];

    genvar mem_idx;
    generate
        for (mem_idx = 0; mem_idx < NUM_MEM; mem_idx = mem_idx + 1) begin : gen_mem
            clk_mux2 u_mem_clk_mux (
                .clk_a   (clk_pll),
                .clk_b   (clk_osc),
                .sel     (clk_mux_sel[mem_idx]),
                .clk_out (mem_mux_clk[mem_idx])
            );

            clk_divider #(
                .DIVIDE_BY (1 << (mem_idx + 1))
            ) u_mem_clk_divider (
                .clk_in  (mem_mux_clk[mem_idx]),
                .rst_n   (rst_n),
                .clk_out (mem_div_clk[mem_idx])
            );

            clk_bypass u_mem_clk_bypass (
                .clk_main   (mem_div_clk[mem_idx]),
                .clk_bypass (mem_mux_clk[mem_idx]),
                .bypass_en  (clk_bypass_en[mem_idx]),
                .clk_out    (mem_clk[mem_idx])
            );

            simple_sram u_mem (
                .CLK (mem_clk[mem_idx]),
                .CEN (mem_cen[mem_idx]),
                .WEN (mem_wen[mem_idx]),
                .A   (mem_addr[mem_idx]),
                .D   (mem_wdata[mem_idx]),
                .Q   (mem_rdata[mem_idx])
            );
        end
    endgenerate
endmodule
