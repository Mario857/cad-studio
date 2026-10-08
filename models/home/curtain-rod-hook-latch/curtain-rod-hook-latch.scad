// Curtain-rod hook v2 - HINGED LATCH GATE (screw or VHB mount)
// Rod drops into an open cup; a gate pivoting on a pin (1.75 mm filament offcut or M2 screw)
// swings down and its barb clicks under a ridge on the cup front. Lifting the rod pushes the
// barb's flat top against the ridge's flat underside, so the gate locks instead of slipping.
// Units mm. In-use coordinates: X = along the rod, Y = out from the frame, Z = up.
// PART = "print"    -> hook + gate laid flat, ready for STL export (print 2 sets)
//        "assembly" -> in-use orientation with a short piece of rod (for viewing only)
//        "hook" / "gate" -> single part, flat

/* [What to show] */
PART = "print";        // ["print", "assembly", "hook", "gate"]
MOUNT = "screw";       // ["screw", "vhb"]
GATE_ANGLE = 0;        // assembly view only: 0 = closed, 90 = open

/* [Rod] */
ROD_D = 10;
ROD_CLEAR = 1.5;
ROD_OFFSET = 15;       // rod axis -> frame face (>= ~14 for this gate layout)

/* [Body] */
WIDTH = 14;
BASE_T = 4;
WALL = 2.4;
FRONT_DROP = 4.5;      // flat cup front extends this far below the rod axis

/* [Gate] */
GATE_T = 2.4;
GATE_GAP = 0.3;        // gate arm above the cup wall top
KNUCKLE_R = 2.6;
PIN_HOOK = 1.8;        // 1.75 filament press fit (use 1.6 for an M2 screw to bite)
PIN_GATE = 2.05;       // free pivot
CLR = 0.4;             // moving clearance
LEG_T = 1.6;
LEG_GAP = 0.2;
RIDGE = 0.65;          // ridge height = barb overlap + 0.05
RIDGE_Z = -3;          // ridge underside relative to the rod axis
TAB = 2.5;             // thumb tab

/* [Mount] */
SCREW_HOLE = 3.9;
CSK_D = 7.2;
SCREW_EDGE = 6;
ACCESS = 4.5;
PLATE_W = 20;

$fn = 72;
R_IN = (ROD_D + ROD_CLEAR) / 2;
R_OUT = R_IN + WALL;
D = ROD_OFFSET;
ZC = SCREW_EDGE + ACCESS + R_OUT;
Z_WALL = ZC + R_IN;
PY = BASE_T + CLR + KNUCKLE_R;
PZ = Z_WALL + GATE_GAP + GATE_T / 2;
Z_BACK = PZ - KNUCKLE_R - CLR;
Z_SCREWS = [SCREW_EDGE, PZ + KNUCKLE_R + ACCESS];
HEIGHT = Z_SCREWS[1] + SCREW_EDGE;
Y_FO = D + R_OUT + 0.4;
Y_LI = Y_FO + RIDGE + LEG_GAP;
ZR = ZC + RIDGE_Z;
BARB = Y_LI - (Y_FO + 0.05);
Z_LEG = ZR - 0.5 - BARB * 1.4 - 1;
G_TOP = Z_WALL + GATE_GAP + GATE_T;

module rect(y0, y1, z0, z1) translate([y0, z0]) square([y1 - y0, z1 - z0]);
module inuse(w, x0 = 0) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(w, convexity = 8) children();
module tear2d(r) { circle(r); translate([r * 0.7071, 0]) rotate(45) square(r, center = true); }
module csk_hole(x, z) {
    r = SCREW_HOLE / 2; h = (CSK_D - SCREW_HOLE) / 2;
    translate([x, 0, z]) {
        translate([0, 50, 0]) rotate([90, 0, 0]) linear_extrude(100, convexity = 4) tear2d(r);
        translate([0, BASE_T - h, 0]) rotate([-90, 0, 0]) cylinder(h = h + 0.01, r1 = r, r2 = CSK_D / 2);
        translate([0, BASE_T, 0]) rotate([-90, 0, 0]) cylinder(h = 1, r = CSK_D / 2);
    }
}
module pin(d) translate([-1, PY, PZ]) rotate([0, 90, 0]) cylinder(d = d, h = WIDTH + 2);

module hook_profile() difference() {
    union() {
        rect(0, BASE_T, 0, HEIGHT);
        rect(0, D - R_IN, ZC - R_OUT, Z_BACK);
        translate([D, ZC]) circle(R_OUT);
        rect(D + R_IN, Y_FO, ZC - FRONT_DROP, Z_WALL);
        polygon([[Y_FO - 0.01, ZR], [Y_FO + RIDGE, ZR], [Y_FO + RIDGE, ZR + 0.6],
                 [Y_FO - 0.01, ZR + 0.6 + RIDGE * 1.5]]);
    }
    translate([D, ZC]) circle(R_IN);
    rect(D - R_IN, D + R_IN, ZC, Z_WALL + 10);
    rect(BASE_T, Y_FO + 2, Z_WALL, Z_WALL + 10);
    rect(BASE_T, D - R_IN, Z_BACK, Z_WALL + 10);
}
module hook_knuckle() { translate([PY, PZ]) circle(KNUCKLE_R); rect(BASE_T - 0.01, PY + KNUCKLE_R * 0.6, Z_BACK - 1, PZ + KNUCKLE_R); }

module hook() difference() {
    union() {
        inuse(WIDTH) hook_profile();
        inuse(WIDTH / 2) hook_knuckle();                 // knuckle on the bed half
        if (MOUNT == "vhb") cube([PLATE_W, BASE_T, HEIGHT]);
    }
    pin(PIN_HOOK);
    if (MOUNT == "screw") for (z = Z_SCREWS) csk_hole(WIDTH / 2, z);
}

module gate_profile() {
    rect(PY + KNUCKLE_R + CLR, Y_LI + LEG_T, Z_WALL + GATE_GAP, G_TOP);
    rect(Y_LI, Y_LI + LEG_T, Z_LEG, G_TOP);
    polygon([[Y_LI + 0.01, ZR - 0.2], [Y_LI - BARB, ZR - 0.2], [Y_LI - BARB, ZR - 0.5],
             [Y_LI + 0.01, ZR - 0.5 - BARB * 1.4]]);
    rect(Y_LI + LEG_T - 0.01, Y_LI + LEG_T + TAB, Z_LEG, Z_LEG + 1.6);
}
module gate_knuckle() { translate([PY, PZ]) circle(KNUCKLE_R); rect(PY, PY + KNUCKLE_R + CLR + 1, PZ - GATE_T / 2, PZ + GATE_T / 2); }

// gate in its closed position (in-use coordinates)
module gate() difference() {
    union() { inuse(WIDTH) gate_profile(); inuse(WIDTH / 2, WIDTH / 2) gate_knuckle(); }
    pin(PIN_GATE);
}
// gate mirrored so its knuckle half sits on the bed
module gate_flat() translate([WIDTH, 0, 0]) mirror([1, 0, 0]) gate();

module rod() color("Gainsboro") translate([-25, D, ZC - ROD_CLEAR / 2]) rotate([0, 90, 0]) cylinder(d = ROD_D, h = 25);

if (PART == "assembly") {
    color("SteelBlue") hook();
    color("Orange") translate([0, PY, PZ]) rotate([GATE_ANGLE, 0, 0]) translate([0, -PY, -PZ]) gate();
    rod();
}
else if (PART == "hook") rotate([0, -90, 0]) hook();
else if (PART == "gate") rotate([0, -90, 0]) gate_flat();
else rotate([0, -90, 0]) { hook(); translate([0, 25, 0]) gate_flat(); }
