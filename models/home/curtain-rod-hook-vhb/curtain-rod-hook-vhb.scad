// Curtain-rod hook v5 - NO-DRILL VHB TAPE + GRAVITY-LOCK SEAT (vhb or screw mount)
// No moving parts: the rod drops down the front channel, then rolls back under the roof into a
// pocket deeper than the channel floor. To escape it must lift, move forward, then lift again -
// a window slam can't do that, and loading/unloading the rod never pulls on the tape.
// Mount: one 19 mm strip of 3M VHB on the 20 x 50 mm plate (IPA-clean, press 30 s, wait 24 h).
// Units mm. In-use coordinates: X = along the rod, Y = out from the frame, Z = up.
// PART = "print"    -> one hook laid flat, ready for STL export (print 2)
//        "assembly" -> in-use orientation with a short piece of rod (for viewing only)

/* [What to show] */
PART = "print";        // ["print", "assembly"]
MOUNT = "vhb";         // ["vhb", "screw"]

/* [Rod] */
ROD_D = 10;
ROD_CLEAR = 1.5;
ROD_OFFSET = 15;

/* [Body] */
PLATE_W = 20;          // plate width (19 mm tape)
PLATE_H = 50;
PLATE_T = 3;
HOOK_W = 12;           // hook width along the rod (flush with the plate's bed side)
HOOK_LIFT = 4;         // hook bottom above plate bottom (hook low = long plate above resists peel)
WALL = 2.4;
SILL = 0.8;            // pocket depth below the channel floor, fraction of the bore radius
ROOF_TIP = 1;          // roof reaches this far past the rod axis
HEAD_CLR = 0.5;        // rod clearance under the roof while rolling into the pocket

/* [Screw option] */
SCREW_HOLE = 3.9;
CSK_D = 7.2;
SCREW_EDGE = 6;
ACCESS = 4.5;

$fn = 72;
R_IN = (ROD_D + ROD_CLEAR) / 2;
R_OUT = R_IN + WALL;
D = ROD_OFFSET;
ZC = HOOK_LIFT + R_OUT;
Z_FLOOR = ZC - R_IN + SILL * R_IN;
Z_ROOF = Z_FLOOR + ROD_D + HEAD_CLR;
Y_RT = D + ROOF_TIP;
Y_CF = Y_RT + ROD_D + ROD_CLEAR;
TOP = Z_ROOF + WALL;
Y1 = Y_CF + WALL;
Z0 = ZC - R_OUT;
Z_SCREWS = [TOP + ACCESS, PLATE_H - SCREW_EDGE];   // screw option: both above the hook

module rect(y0, y1, z0, z1) translate([y0, z0]) square([y1 - y0, z1 - z0]);
module inuse(w, x0 = 0) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(w, convexity = 8) children();
module tear2d(r) { circle(r); translate([r * 0.7071, 0]) rotate(45) square(r, center = true); }
module csk_hole(x, z) {
    r = SCREW_HOLE / 2; h = (CSK_D - SCREW_HOLE) / 2;
    translate([x, 0, z]) {
        translate([0, 50, 0]) rotate([90, 0, 0]) linear_extrude(100, convexity = 4) tear2d(r);
        translate([0, PLATE_T - h, 0]) rotate([-90, 0, 0]) cylinder(h = h + 0.01, r1 = r, r2 = CSK_D / 2);
        translate([0, PLATE_T, 0]) rotate([-90, 0, 0]) cylinder(h = 1, r = CSK_D / 2);
    }
}

module profile() difference() {
    union() {
        rect(0, Y1, Z0 + 2, TOP);
        rect(0, Y1, Z0, ZC);
        translate([D, ZC]) circle(R_OUT);
    }
    translate([D, ZC]) circle(R_IN);                 // pocket
    rect(D - R_IN, Y_CF, ZC, Z_ROOF);                // headroom under the roof
    rect(D, Y_CF, Z_FLOOR, ZC + 0.01);               // channel floor level
    rect(Y_RT, Y_CF, Z_ROOF - 0.01, TOP + 1);        // entry channel
    polygon([[Y1 - 6, Z0 - 0.01], [Y1 + 0.01, Z0 - 0.01], [Y1 + 0.01, Z0 + 6]]);
}

module hook() difference() {
    union() {
        inuse(HOOK_W) profile();
        cube([PLATE_W, PLATE_T, PLATE_H]);
    }
    if (MOUNT == "screw") for (z = Z_SCREWS) csk_hole(PLATE_W / 2, z);
}

module rod() color("Gainsboro") translate([-25, D, ZC - ROD_CLEAR / 2]) rotate([0, 90, 0]) cylinder(d = ROD_D, h = 25);

if (PART == "print") rotate([0, -90, 0]) hook();
else { color("SteelBlue") hook(); rod(); }
