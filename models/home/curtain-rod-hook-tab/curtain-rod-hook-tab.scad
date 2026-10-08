// Curtain-rod hook v4 - SPRING TAB WITH THUMB RELEASE (screw or VHB mount)
// The back of the mouth is rigid; the front of the cup is one long spring tab (the ring's front
// half, tied to the base only at the bottom). Push the rod down: the leaning thumb fin funnels
// it, the tab springs 1.2 mm forward and clicks back. To remove, pull the fin forward and lift.
// Units mm. In-use coordinates: X = along the rod, Y = out from the frame, Z = up.
// PART = "print"    -> one hook laid flat, ready for STL export (print 2)
//        "assembly" -> in-use orientation with a short piece of rod (for viewing only)

/* [What to show] */
PART = "print";        // ["print", "assembly"]
MOUNT = "screw";       // ["screw", "vhb"]

/* [Rod] */
ROD_D = 10;
ROD_CLEAR = 1.5;
ROD_OFFSET = 15;
SNAP = 1.2;            // mouth narrower than the rod (all taken by the front tab)
BACK_LIP = 0.75;       // rigid back edge overlaps the bore by this much

/* [Body] */
WIDTH = 14;
BASE_T = 4;
WALL = 2.4;
BAR_T = 3;
FIN_T = 2.4;           // thumb fin
FIN_TOP = 9.5;         // fin top above the rod axis
FIN_LEAN = 3;          // forward lean of the fin

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
Y_B = D - R_IN + BACK_LIP;
Y_N = Y_B + ROD_D - SNAP;
Z_BACK = ZC + 6;
Z_SCREWS = [SCREW_EDGE, ZC + FIN_TOP + ACCESS];
HEIGHT = Z_SCREWS[1] + SCREW_EDGE;
Z_TIP = ZC + 4.4;

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

module profile() difference() {
    union() {
        rect(0, BASE_T, 0, HEIGHT);
        rect(0, D, ZC - R_OUT, ZC - R_OUT + BAR_T);
        rect(0, Y_B, ZC - R_OUT, Z_BACK);
        translate([D, ZC]) circle(R_OUT);
        polygon([[Y_N, Z_TIP], [Y_N + FIN_T + 0.3, Z_TIP - 0.4],
                 [Y_N + FIN_T + 0.3 + FIN_LEAN, ZC + FIN_TOP], [Y_N + FIN_LEAN, ZC + FIN_TOP]]);
    }
    translate([D, ZC]) circle(R_IN);
    rect(Y_B, Y_N, ZC, ZC + FIN_TOP + 1);
    rect(BASE_T, Y_B + 0.01, Z_BACK, ZC + R_OUT + 1);
    polygon([[Y_B - 2, Z_BACK + 0.01], [Y_B + 0.01, Z_BACK + 0.01], [Y_B + 0.01, Z_BACK - 2]]);
}

module hook() difference() {
    union() {
        inuse(WIDTH) profile();
        if (MOUNT == "vhb") cube([PLATE_W, BASE_T, HEIGHT]);
    }
    if (MOUNT == "screw") for (z = Z_SCREWS) csk_hole(WIDTH / 2, z);
}

module rod() color("Gainsboro") translate([-25, D, ZC - ROD_CLEAR / 2]) rotate([0, 90, 0]) cylinder(d = ROD_D, h = 25);

if (PART == "print") rotate([0, -90, 0]) hook();
else { color("SteelBlue") hook(); rod(); }
