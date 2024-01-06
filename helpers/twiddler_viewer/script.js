let layoutGrid = document.getElementById('layout-grid');

let data = [
    ['MOOO', '.'],
    ['LOOO', '<Space>'],
    ['LROO', '<Tab>'],
    ['LLOO', '<Backspace>'],
    ['ORRO', 'f'],
    ['OMRO', 'y'],
    ['OOMO', 'o'],
    ['ORMO', 'g'],
    ['OMLO', 't'],
    ['OOOR', '<Return>'],
    ['OROR', 'c'],
    ['OMOR', 'h'],
    ['OLOR', 'l'],
    ['OORR', 'a'],
    ['ORRR', 'e'],
    ['OOMR', 'n'],
    ['ORMR', 'k'],
    ['OMMR', 'r'],
    ['OLMR', 'x'],
    ['OOLR', 'u'],
    ['OROM', 'j'],
    ['OMOM', 'i'],
    ['OLOM', 'v'],
    ['OORM', 'p'],
    ['OOMM', 'b'],
    ['ORMM', 's'],
    ['OMMM', 'm'],
    ['OOLM', 'z'],
    ['OOOL', '<escape>'],
    ['OOML', 'q'],
    ['OOLL', 'd'],
    ['OLLL', 'w']
];

data.forEach(([markings, letter]) => {
    let newItem = document.createElement('div');
    newItem.className = 'col-lg-3 col-md-4 col-sm-6 p-2';
    
    let label = document.createElement('p');
    label.className = 'grid-label';
    label.innerText = letter;
    newItem.appendChild(label);

    let newGrid = document.createElement('div');
    newGrid.className = 'grid';
    newItem.appendChild(newGrid);
    
    
    for (let row = 0; row < 4; row++) { // For each row
     for(let col=0; col<3; col++){ // For each column
         let square = document.createElement('div');
         square.classList.add('square'); // Add 'square' as a common class for all cells

         switch (markings.charAt(row)) {
             case 'O': break;
             case 'L': if (col === 0) square.classList.add('marked'); break;
             case 'M': if (col === 1) square.classList.add('marked'); break;
             case 'R': if (col === 2) square.classList.add('marked'); break;
         }
         newGrid.appendChild(square);
     }
}


    
    layoutGrid.appendChild(newItem);
});