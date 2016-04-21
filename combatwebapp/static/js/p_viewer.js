/**
 * Created by thoba on 2016/04/21.
 */
// override the default options with something less restrictive.
// var options = {
//   width: 600,
//   height: 600,
//   antialias: true,
//   quality : 'medium'
// };
// // insert the viewer under the Dom element with id 'gl'.
// var viewer = pv.Viewer(document.getElementById('viewer'), options);
//
// function loadMethylTransferase() {
//   // asynchronously load the PDB file for the dengue methyl transferase
//   // from the server and display it in the viewer.
//   pv.io.fetchPdb("http://files.rcsb.org/view/1GN2.pdb", function(structure) {
//       // display the protein as cartoon, coloring the secondary structure
//       // elements in a rainbow gradient.
//       viewer.cartoon('protein', structure, { color : color.ssSuccession() });
//       // there are two ligands in the structure, the co-factor S-adenosyl
//       // homocysteine and the inhibitor ribavirin-5' triphosphate. They have
//       // the three-letter codes SAH and RVP, respectively. Let's display them
//       // with balls and sticks.
//       var ligands = structure.select({ rnames : ['SAH', 'RVP'] });
//       viewer.ballsAndSticks('ligands', ligands);
//       viewer.centerOn(structure);
//   });
// }
//
// // load the methyl transferase once the DOM has finished loading. That's
// // the earliest point the WebGL context is available.
// document.addEventListener('DOMContentLoaded', loadMethylTransferase);

//EXAMPLE
var parent = document.getElementById('viewer');
var viewer = pv.Viewer(parent,
    {width: 1280, height: 600, antialias: true});


function setColorForAtom(go, atom, color) {
    var view = go.structure().createEmptyView();
    view.addAtom(atom);
    go.colorBy(pv.color.uniform(color), view);
}

// variable to store the previously picked atom. Required for resetting the color
// whenever the mouse moves.
var prevPicked = null;
// add mouse move event listener to the div element containing the viewer. Whenever
// the mouse moves, use viewer.pick() to get the current atom under the cursor.
parent.addEventListener('mousemove', function (event) {
    var rect = viewer.boundingClientRect();
    var picked = viewer.pick({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    });
    if (prevPicked !== null && picked !== null &&
        picked.target() === prevPicked.atom) {
        return;
    }
    if (prevPicked !== null) {
        // reset color of previously picked atom.
        setColorForAtom(prevPicked.node, prevPicked.atom, prevPicked.color);
    }
    if (picked !== null) {
        var atom = picked.target();
        document.getElementById('picked-atom-name').innerHTML = atom.qualifiedName();
        // get RGBA color and store in the color array, so we know what it was
        // before changing it to the highlight color.
        var color = [0, 0, 0, 0];
        picked.node().getColorForAtom(atom, color);
        prevPicked = {atom: atom, color: color, node: picked.node()};

        setColorForAtom(picked.node(), atom, 'red');
    } else {
        document.getElementById('picked-atom-name').innerHTML = '&nbsp;';
        prevPicked = null;
    }
    viewer.requestRedraw();
});

var id = $("#pdb_id").text();

pv.io.fetchPdb("http://files.rcsb.org/view/"+id+".pdb", function (structure) {
    // put this in the viewerReady block to make sure we don't try to add the
    // object before the viewer is ready. In case the viewer is completely
    // loaded, the function will be immediately executed.
    viewer.on('viewerReady', function () {
        var go = viewer.cartoon('structure', structure);
        // adjust center of view and zoom such that all structures can be seen.
        viewer.autoZoom();
    });
});