function sortTable(n) {
	var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
	table = document.getElementById("datatable");
	switching = true;
	//Set the sorting direction to ascending:
	dir = "asc"; 

	while (switching) {

	  switching = false;
	  rows = table.rows;

	  for (i = 1; i < (rows.length - 1); i++) {

		shouldSwitch = false;

		x = rows[i].getElementsByTagName("TD")[n];
		y = rows[i + 1].getElementsByTagName("TD")[n];
		/*check if the two rows should switch place,
		based on the direction, asc or desc:*/
		if (dir == "asc") {
		  if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
			//if so, mark as a switch and break the loop:
			shouldSwitch= true;
			break;
		  }
		} else if (dir == "desc") {
		  if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
			//if so, mark as a switch and break the loop:
			shouldSwitch = true;
			break;
		  }
		}
	  }
	  if (shouldSwitch) {
		/*If a switch has been marked, make the switch
		and mark that a switch has been done:*/
		rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
		switching = true;
		//Each time a switch is done, increase this count by 1:
		switchcount ++;      
	  } else {
		/*If no switching has been done AND the direction is "asc",
		set the direction to "desc" and run the while loop again.*/
		if (switchcount == 0 && dir == "asc") {
		  dir = "desc";
		  switching = true;
		}
	  }
	}
  }
  $('.search-toggle').click(function() {
    if ($('.hiddensearch').css('display') == 'none')
      console.log('ffff');
    else
      $('.hiddensearch').slideUp();
  });

  /* Set the defaults for DataTables initialisation */
  $.extend(true, DataTable.defaults, {
    dom: "<'hiddensearch'f'>" +
      "tr" +
      "<'table-footer'lip'>",
    renderer: 'material'
  });

  /* Default class modification */
  $.extend(DataTable.ext.classes, {
    sWrapper: "dataTables_wrapper",
    sFilterInput: "form-control input-sm",
    sLengthSelect: "form-control input-sm"
  });