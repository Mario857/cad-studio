// Curtain-rod hook v1 - SNAP-FIT C-CLIP (screw or VHB mount)
// Push the rod down through the funnel: the C-ring lips spread 1.2 mm and click shut.
// Units mm. In-use coordinates: X = along the rod, Y = out from the frame, Z = up.
// PART = "print"   -> one hook laid flat, ready for STL export (print 2)
//        "assembly" -> in-use orientation with a short piece of rod (for viewing only)

/* [What to show] */
PART = "print";        // ["print", "assembly"]
MOUNT = "screw";       // ["screw", "vhb"]

/* [Rod] */
ROD_D = 10;            // rod diameter
ROD_CLEAR = 1.5;       // diametral clearance (rod turns/slides freely)
ROD_OFFSET = 15;       // rod axis -> frame face
SNAP = 1.2;            // mouth is this much narrower than the rod (1.0-1.5 for ASA/ABS)

/* [Body] */
WIDTH = 14;            // along the rod (= base width on the frame)
BASE_T = 4;            // base plate thickness
WALL = 2.4;            // ring wall
BAR_T = 3;             // web tying the ring bottom to the base
FUNNEL = 3;            // 45 deg lead-in above the lips

/* [Mount] */
SCREW_HOLE = 3.9;      // clearance for 3.5 mm self-tapping screw
CSK_D = 7.2;           // 90 deg countersink diameter
SCREW_EDGE = 6;        // screw axis from base end
ACCESS = 4.5;          // screw axis to nearest hook feature (screwdriver room)
PLATE_W = 20;          // VHB plate width (19 mm tape)

$fn = 72;
R_IN = (ROD_D + ROD_CLEAR) / 2;
R_OUT = R_IN + WALL;
D = ROD_OFFSET;
ZC = SCREW_EDGE + ACCESS + R_OUT;
Z_SCREWS = [SCREW_EDGE, ZC + R_OUT + ACCESS];
HEIGHT = Z_SCREWS[1] + SCREW_EDGE;
MOUTH = ROD_D - SNAP;
ZF = ZC + R_IN * 0.75;

module rect(y0, y1, z0, z1) translate([y0, z0]) square([y1 - y0, z1 - z0]);
// 2D profile (u = Y, v = Z) extruded along X from x0
module inuse(w, x0 = 0) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(w, convexity = 8) children();
module tear2d(r) { circle(r); translate([r * 0.7071, 0]) rotate(45) square(r, center = true); }

// countersunk hole along Y, head at the base front, teardrop tip toward +X (up when printed)
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
        translate([D, ZC]) circle(R_OUT);
    }
    translate([D, ZC]) circle(R_IN);
    rect(D - MOUTH / 2, D + MOUTH / 2, ZC, ZC + R_OUT + 1);
    polygon([[D - MOUTH / 2, ZF], [D + MOUTH / 2, ZF],
             [D + MOUTH / 2 + FUNNEL, ZF + FUNNEL], [D - MOUTH / 2 - FUNNEL, ZF + FUNNEL]]);
}

module hook() difference() {
    union() {
        inuse(WIDTH) profile();
        if (MOUNT == "vhb") cube([PLATE_W, BASE_T, HEIGHT]);
    }
    if (MOUNT == "screw") for (z = Z_SCREWS) csk_hole(WIDTH / 2, z);
}

module rod() color("Gainsboro") translate([-25, D, ZC - ROD_CLEAR / 2]) rotate([0, 90, 0]) cylinder(d = ROD_D, h = 25);

if (PART == "print") rotate([0, -90, 0]) hook();   // x = 0 side face on the bed
else { color("SteelBlue") hook(); rod(); }
