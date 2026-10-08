// Curtain-rod hook v3 - SCREW-SECURED CAP / CLAMP (screw or VHB mount)
// Drop the rod in, slide the cap on sideways (its front hook runs along the ledge on the cup
// front), then fix its back with one M3 x 8 screw into an M3 heat-set insert. Closed loop.
// CLAMP_PAD sets how far the cap's pad reaches into the bore: < ROD_CLEAR leaves the rod free,
// >= ROD_CLEAR grips it so it can't slide or rattle.
// Units mm. In-use coordinates: X = along the rod, Y = out from the frame, Z = up.
// PART = "print"    -> hook + cap laid flat, ready for STL export (print 2 sets)
//        "assembly" -> in-use orientation with a short piece of rod (for viewing only)
//        "hook" / "cap" -> single part, flat

/* [What to show] */
PART = "print";        // ["print", "assembly", "hook", "cap"]
MOUNT = "screw";       // ["screw", "vhb"]

/* [Rod] */
ROD_D = 10;
ROD_CLEAR = 1.5;
ROD_OFFSET = 15;

/* [Body] */
WIDTH = 14;
BASE_T = 4;
WALL = 2.4;

/* [Cap] */
CAP_T = 3;
CLAMP_PAD = 1.0;       // 1.0 = rod free with 0.5 mm play; 1.5+ = clamped
LEDGE = 1.6;
LEDGE_T = 1.6;
HOOK_T = 1.8;
CLR = 0.3;
INSERT_D = 4.0;        // M3 heat-set insert hole (check your insert's spec)
INSERT_DEPTH = 6;
M3_CLEAR = 3.4;

/* [Mount] */
SCREW_HOLE = 3.9;
CSK_D = 7.2;
SCREW_EDGE = 6;
SCREW_PITCH = 12;      // both mount screws sit below the cup
ACCESS = 4.5;
PLATE_W = 20;

$fn = 72;
R_IN = (ROD_D + ROD_CLEAR) / 2;
R_OUT = R_IN + WALL;
D = ROD_OFFSET;
Z_SCREWS = [SCREW_EDGE, SCREW_EDGE + SCREW_PITCH];
ZC = Z_SCREWS[1] + ACCESS + R_OUT;
Z_WALL = ZC + R_IN;
Y_FO = D + R_OUT + 0.4;
Y_S = (D - R_IN) / 2;
Y_LEG = Y_FO + LEDGE + CLR;
Z_LIP = Z_WALL - LEDGE_T - CLR;

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
// vertical (in use) teardrop hole from z_top down
module v_hole(d, y, z_top, depth) translate([WIDTH / 2, y, z_top - depth]) linear_extrude(depth + 1, convexity = 4) tear2d(d / 2);

module hook_profile() difference() {
    union() {
        rect(0, BASE_T, 0, Z_WALL);
        rect(0, D - R_IN, ZC - R_OUT, Z_WALL);
        translate([D, ZC]) circle(R_OUT);
        rect(D + R_IN, Y_FO, ZC - 2, Z_WALL);
        rect(Y_FO - 0.01, Y_FO + LEDGE, Z_WALL - LEDGE_T, Z_WALL);
    }
    translate([D, ZC]) circle(R_IN);
    rect(D - R_IN, D + R_IN, ZC, Z_WALL + 1);
    rect(-1, Y_FO + LEDGE + 1, Z_WALL, Z_WALL + R_OUT);
}
module hook() difference() {
    union() {
        inuse(WIDTH) hook_profile();
        if (MOUNT == "vhb") cube([PLATE_W, BASE_T, Z_WALL]);
    }
    v_hole(INSERT_D, Y_S, Z_WALL, INSERT_DEPTH);
    if (MOUNT == "screw") for (z = Z_SCREWS) csk_hole(WIDTH / 2, z);
}

module cap_profile() {
    rect(0, Y_LEG + HOOK_T, Z_WALL, Z_WALL + CAP_T);
    rect(Y_LEG, Y_LEG + HOOK_T, Z_LIP - HOOK_T, Z_WALL + 0.01);
    rect(Y_FO + CLR, Y_LEG + 0.01, Z_LIP - HOOK_T, Z_LIP);
    if (CLAMP_PAD > 0) rect(D - 3, D + 3, Z_WALL - CLAMP_PAD, Z_WALL + 0.01);
}
module cap() difference() {
    inuse(WIDTH) cap_profile();
    v_hole(M3_CLEAR, Y_S, Z_WALL + CAP_T + 1, CAP_T + 2);
}

module rod() color("Gainsboro") translate([-25, D, ZC - ROD_CLEAR / 2]) rotate([0, 90, 0]) cylinder(d = ROD_D, h = 25);

if (PART == "assembly") { color("SteelBlue") hook(); color("Orange") cap(); rod(); }
else if (PART == "hook") rotate([0, -90, 0]) hook();
else if (PART == "cap") rotate([0, -90, 0]) cap();
else rotate([0, -90, 0]) { hook(); translate([0, 32, 0]) cap(); }
