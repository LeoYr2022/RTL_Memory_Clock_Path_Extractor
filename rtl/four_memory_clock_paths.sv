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
    input  wire        clk_pll0,
    input  wire        clk_pll1,
    input  wire        clk_osc0,
    input  wire        clk_osc1,
    input  wire        clk_test0,
    input  wire        clk_test1,
    input  wire        clk_scan0,
    input  wire        clk_scan1,
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
    wire mem0_mux_clk;
    wire mem0_div_clk;
    wire mem0_clk;

    wire mem1_mux_clk;
    wire mem1_div_clk;
    wire mem1_clk;

    wire mem2_mux_clk;
    wire mem2_div_clk;
    wire mem2_clk;

    wire mem3_mux_clk;
    wire mem3_div_clk;
    wire mem3_clk;

    clk_mux2 u_mem0_clk_mux (
        .clk_a   (clk_pll0),
        .clk_b   (clk_osc0),
        .sel     (clk_mux_sel[0]),
        .clk_out (mem0_mux_clk)
    );

    clk_divider #(
        .DIVIDE_BY (2)
    ) u_mem0_clk_divider (
        .clk_in  (mem0_mux_clk),
        .rst_n   (rst_n),
        .clk_out (mem0_div_clk)
    );

    clk_bypass u_mem0_clk_bypass (
        .clk_main   (mem0_div_clk),
        .clk_bypass (mem0_mux_clk),
        .bypass_en  (clk_bypass_en[0]),
        .clk_out    (mem0_clk)
    );

    simple_sram u_mem0 (
        .CLK (mem0_clk),
        .CEN (mem_cen[0]),
        .WEN (mem_wen[0]),
        .A   (mem0_addr),
        .D   (mem0_wdata),
        .Q   (mem0_rdata)
    );

    clk_mux2 u_mem1_clk_mux (
        .clk_a   (clk_pll1),
        .clk_b   (clk_osc1),
        .sel     (clk_mux_sel[1]),
        .clk_out (mem1_mux_clk)
    );

    clk_divider #(
        .DIVIDE_BY (4)
    ) u_mem1_clk_divider (
        .clk_in  (mem1_mux_clk),
        .rst_n   (rst_n),
        .clk_out (mem1_div_clk)
    );

    clk_bypass u_mem1_clk_bypass (
        .clk_main   (mem1_div_clk),
        .clk_bypass (mem1_mux_clk),
        .bypass_en  (clk_bypass_en[1]),
        .clk_out    (mem1_clk)
    );

    simple_sram u_mem1 (
        .CLK (mem1_clk),
        .CEN (mem_cen[1]),
        .WEN (mem_wen[1]),
        .A   (mem1_addr),
        .D   (mem1_wdata),
        .Q   (mem1_rdata)
    );

    clk_mux2 u_mem2_clk_mux (
        .clk_a   (clk_test0),
        .clk_b   (clk_scan0),
        .sel     (clk_mux_sel[2]),
        .clk_out (mem2_mux_clk)
    );

    clk_divider #(
        .DIVIDE_BY (8)
    ) u_mem2_clk_divider (
        .clk_in  (mem2_mux_clk),
        .rst_n   (rst_n),
        .clk_out (mem2_div_clk)
    );

    clk_bypass u_mem2_clk_bypass (
        .clk_main   (mem2_div_clk),
        .clk_bypass (mem2_mux_clk),
        .bypass_en  (clk_bypass_en[2]),
        .clk_out    (mem2_clk)
    );

    simple_sram u_mem2 (
        .CLK (mem2_clk),
        .CEN (mem_cen[2]),
        .WEN (mem_wen[2]),
        .A   (mem2_addr),
        .D   (mem2_wdata),
        .Q   (mem2_rdata)
    );

    clk_mux2 u_mem3_clk_mux (
        .clk_a   (clk_test1),
        .clk_b   (clk_scan1),
        .sel     (clk_mux_sel[3]),
        .clk_out (mem3_mux_clk)
    );

    clk_divider #(
        .DIVIDE_BY (16)
    ) u_mem3_clk_divider (
        .clk_in  (mem3_mux_clk),
        .rst_n   (rst_n),
        .clk_out (mem3_div_clk)
    );

    clk_bypass u_mem3_clk_bypass (
        .clk_main   (mem3_div_clk),
        .clk_bypass (mem3_mux_clk),
        .bypass_en  (clk_bypass_en[3]),
        .clk_out    (mem3_clk)
    );

    simple_sram u_mem3 (
        .CLK (mem3_clk),
        .CEN (mem_cen[3]),
        .WEN (mem_wen[3]),
        .A   (mem3_addr),
        .D   (mem3_wdata),
        .Q   (mem3_rdata)
    );
endmodule
