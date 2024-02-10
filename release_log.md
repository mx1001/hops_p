## 0.0.9.8.4.2 Neodymium_11
- lattice improvements (lF)
- to_box improvements (lF)
- ~ to toggle viewport off
- material scroll
- blank material edit mode
- late parent proper (lF)
- bevel vert in edit mode adjustment

## 0.0.9.8.4.2 Neodymium_10

	- Add Camera Improvements
		○ F9 Window
		○ Rotation Parameter
		○ Added to neutral Q menu
		○ Frontal positioning by default
		○ B7 System to avoid driver complaints
		○ Toggle for set to active cam (also on CTRL)
		○ (TRACK TO CONSTRAINT IS NOT NEEDED) maybe remove
	- Radial Array Improvements
		○ Cursor resume adjustment now more graceful
		○ Functionality Improvements
	- To Plane
		○ Active Selection on addition
	- To Box
		○ Awaiting improvements
	- Bevel Improvements
		○ X - sets to half of last bevel mod present
		○ Alt + X - sets bevel to half of active bevel
	- Step Improvements
		○ Rebuilt for Weight workflow
			§ Due to lack of sstate the previous workflow remains incomplete.
		○ Bevel half for angle workflow
	- HOPStool cleanup
		○ Verbiage
		○ Curve tool error
	- Icons re-vamp P1
		○ More icons to come
	- Alt + V improvements
		○ Solid / Texture toggle added to alt + V
	-  Sharpen Improvements
		○ WN to tooltip
	- Smart Apply Modifier Improvements
		○ Shift + Click will apply all while removing last bevel and WN. Useful for surface extraction.
	- Menu Adjustments
		○ Clear Sharp re-added (sorry about that)
	- Clear Sharp Improvements
		○ Option for clear mesh data.
Spacebar option to clear custom normal data

## 0.0.9.8.4.2
- Dice V2
  ○ Intersect or knife behavior
  ○ Helper options for pre-emptive behavior
- Radial Array v3
  ○ All in one.
  ○ Capable of repeat working in an area w/ cursor
- Blank Material (ramp / carpaint)
  ○ Ramp shader w/ special controls
  ○ Carpaint w/ special controls
- Camera Turntable
  ○ Perfect turntable
- Bugfixes
Random errors w/ bevel, mirror, array.

## 0.0.9.8.4.1
- Atwist 361
Dice V1 (concept)
- Step (nondestructive)
- Bevel
  ○ C (clamp overlap) / shift + C loop slide.
- Direct shift (pie)
- Smart apply improvements
- Blank Material Expanded V3
  ○ Emission Pulse / Glass
- HOPStool improvements
  ○ Text / text size
  ○ Boolshape parent
  ○ D helper (temp)
    § Cursor snap box
  ○ Smart shape improvements (2.82+)
  ○ Vertex shape
  ○ Array 1, 2, 3 hotkey in modal w/ dot
- Menu Changes

## 0.0.9.8.4

HOPS 984
	- Curve res added to Q menu
	- Interior bevel support
	- Edit Mode Slice Added
		○ Knife Added
		○ Inset Added
	- Object Mode Inset Added
			§ Alt + shift + numpad slash hotkey
		○ Outset toggle
		○ Slice Added
	- Sort V3 added w/ sync
	- 2.82 Array and mirror gizmo fixed
	- Bevel Helper angle fix
	- Weighted normal multi support +
	- Lazy Support for mod modals
	- Radial Array Ctrl fix for displacement mod
	- Lamp options added to Q menu and pie
	- Random material V2
	- 2d bevel to bevel w/ weld support
	- Late Parent
	- Reset Axis
	- Sharpen
	- Array Support for plane
	- To Box V1 added
	- Ctrl + Shift + B
		○ Smart Key
			§ Boolshape
				□ Boolshift
			§ Bevel
				□ Helper
			§ Pend Bool
				□ BoolScroll
			§ 2 Ob
				□ Diff
			§ 3 Ob
				□ Slash
	- Interactive Boolean Operation
	- Smooth / Laplacian Mod support
		○ Shift Support for special sharp vgroup
	- Meta ball to helper
	- Mirror / Array consolidation
	- Boolean bypass
	- Hotkey corrections for sort
	- Smart apply V2
	- Directors Cut
		○ Bool auto sort WN
		○ hT - 2d bevel weld sort ignore
		○ Sharpen out of boolshapes menu
		○ Boolscroll out of edit mode (unstable) (experimental)
		○ Union fix
		○ Sharp Manager to default bevel helper
X Toggles shape in modscroll

- Weld support added to 2d bevel along w/ clamp overlap
- Radial Array Ctrl fix for displacement mod w/ 3d cursor
- Lamp options added to Q menu and pie
- Random material V2 (random mats per object w/ toolbox)
- Shift Bool added
- Sharpen consolidation
- Scroll consolidation
- mirror / array consolidation
- Hops tool boolean ring
- displace disabled for ctrl w/ radial array 3d cursor
- bevel WN sort behavior
- boolean sort override toggle and hotkey
- bwidth dimension check to replace 2d bevel
- knife / knife project support
- knife dimension check to toggle knife project

12/11/19
- Curve res added to Q menu
- Interior bevel support
- Edit Mode Slice Added
  - Knife Added
  - Inset Added
- Object Mode Inset Added
    - Alt + shift + numpad slash hotkey
  - Outset toggle
  - Slice Added
- Sort V3 added w/ sync
- 2.82 Array and mirror gizmo fixed
- Bevel Helper angle fix
- Weighted normal multi support +
- Lazy Support for mod modals

### 0.0.9.8.3
- curve res added to Q menu
- hops helper curve fixed
- mod toggle working on all selected objects
- bisect shift option on mirror
- csharp no longer applies last bevel not / mod updated
- array fixes
- circle dot fix
- boolean dots show for only active object
- new options added to shift + G
- Eevee LQ / HQ lvl 2
- 2.82 topbar label fix
- blank material V2

- hardFlow panel
	○ Dot Modifiers
- hardShape system V1
- Scroll fixes
- Boolshapes for active object only in hopstool
Helper support for curve and text

### 0.0.9.5
    - loop slide option for Bweight added (helper)
- modal mirror operator added
    - fix for auto smooth overwrite
- default for auto smooth changed to 180
- fix for brush preview error
- MESHmachine integration in edit mode operations
    - shrinkwrap refresh is hidden for now
- boolean operators added to edit mode under operations
- mir2 cstep support
- spherecast V1 added to meshtools
- QArray supports multiple objects
- TThick supports multiple objects
- misc panel has options for Qarray and Tthick
- Boolean scroll systems added
- basic Kitops support for Csharpen

### 0.0.9.4
- tooltip update
- added hotkeys for edit mode booleans
- rewrite of mirror operator
- new operator added allowing to swap green/red boolshape status (in pie/menu when boolshape is selected)
    -red / green boolean system
        -still needs a smash all booleans bypassing the red/green system
- new boolshape status added allowing to skip applying boolean modifiers
- brush selector added to sculpt menu
- bwidth limit is unlocked for undefined meshes

### 0.0.9.3
- pie menu missing options added
- cut-in operator added
    -cut in added to Q menu. Still needs hotkey
    -context for cut in fixed no single select option
- all inserts now use principal shaders as proxies
- fixed B-width Z wire show mode
- additional icons added
- renderset1 fix for filmic official
- material helper fix for new materials
- relink mirror options added
- figet support added
- new clean mesh operator (options in helper)
- adaptive width mode addeded
- adaptive segments mode adeded

### 0.0.9.2
- hoteys can be set in options hotkey tab
- scale option for modal operators was added
- booleans solver is global now can be set helper
- ssharp, cstep, csharp work on multi objects now (old multi operators removed)
- bool options added to menu/panel
- added 'reset axis' operator
- version bump.
- all operators support step workflow fromn ow on
- s/cstep operators removed and replaced by step
- wire options added to HOPS Helper
- sharpness angle for sharp operator is now global (acces via Tpanel/helper/F6)
- mesh display toggle added to edtimode >> meshtools
- pro mode switches clean ssharp with demote for reason....
- machin3 decal support added

### 0.0.8.7
- Multiple object support for B-Width
- New operator 'bevel multiplier' added
- Hud indicator moved from text to logo by default
	1. logo in corner added
	2. text status disabled by default
	3. added preferences to enable/disable logo/statustext (logo under extra / pro mode)
	4. preferences to change logo color/placement
- new operator - sharp manager was added
- csharpen uses global sharps now
- ssharpen uses global sharps now
- set sharp uses global sharps now
- added new global way to define what sharp edges to use (T-panel/ helper-misc)
- SUB-d status removed from all operators (use global statuses now)
- bweight can now select all other bweight edges in object while in modal state by presing A
- BOOLSHAPE objects are hiden to renderer now (outliner icon)
- slash assigns boolshape status for cutters now
- panels/menus/pie updated with correct operators
- added option for slash to refresh origin of cutters (in F6)
- Slice and rebbol operators replaces with slash
- fixes for material cutting
- renderset C created (speed preset)
- fix for register bug (hotkeys duplication)
- pie menu and menu uses same hotkey now (Q) it can be chosen in preferences
