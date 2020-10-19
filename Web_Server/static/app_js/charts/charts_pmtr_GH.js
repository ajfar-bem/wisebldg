/**

 *  Authors: Kruthika Rathinavel
 *  Version: 2.0
 *  Email: kruthika@vt.edu
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"


 * Copyright © 2014 by Virginia Polytechnic Institute and State University
 * All rights reserved

 * Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
 * associated documentation ("Software") and retains rights to grant research rights under patents related to
 * the BEMOSS software to other academic institutions or non-profit research institutions.
 * You should carefully read the following terms and conditions before using this software.
 * Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

 * You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
 * use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
 * the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
 * licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
 * for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
 * without fee, subject to the following terms of this license.

 * Commercial Use: If you desire to use the software for profit-making or commercial purposes,
 * you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
 * Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
 * licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org

 * Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
 * THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
 * LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
 * OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGES.

 * For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

 * Address all correspondence regarding this license to Virginia Tech's electronic mail address:: vtippatents@vtip.org

**/

$(document).ready(function(){
    $.csrftoken();

    /**
     * Plot functions and values for Power
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */

	  //Plot options
	  var options_power = {
			    legend: {
			      show: true,
			      labels:["Minisplits 1 ", "Minisplits 2", "Minisplits 3", "Minisplits 4","Power "]
			    },
                series:[{
                    label: 'Power (kW)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                }],
			    cursor: {
			           show: true,
			           zoom: true
			    },
			    seriesDefaults: {
                  show: true,
			      showMarker:false,
			      pointLabels: {show:false},
			      rendererOption:{smooth: true}
			    },
			    axesDefaults: {
			      labelRenderer: $.jqplot.CanvasAxisLabelRenderer
			    },
			    axes: {
			      xaxis: {
			        label: "Time",
			        renderer: $.jqplot.DateAxisRenderer,
			        tickOptions:{formatString:'%m/%d, %H:%M'},
			        numberTicks: 10,
		            min : _power_sum[0][0],
		            max: _power_sum[_power_sum.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Power (kW)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_power = [_power_a, _power_b, _power_c, _power_ac, _power_sum];
	  var plot_power = $.jqplot('chart100', data_points_power ,options_power);
      $("#power_sum").attr('checked','checked');
      $("#power_a").attr('checked','checked');
      $("#power_b").attr('checked','checked');
      $("#power_c").attr('checked','checked');
$("#power_ac").attr('checked','checked');
      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {

            },
            axesStyles: {
               borderWidth: 0,
               label: {
                   fontFamily: 'Sans',
                   textColor: 'white',
                   fontSize: '9pt'
               }
            }
        };


        plot_power.themeEngine.newTheme('uma', temp);
        plot_power.activateTheme('uma');

        var timeOut_power;

        function update_plot_power(_data) {
            var _power_sum = _data.power;
           // _power_sum = $.parseJSON(_power_sum);
            var _power_a = _data.power_a;
            //_power_a = $.parseJSON(_power_a);
            var _power_b = _data.power_b;
           // _power_b = $.parseJSON(_power_b);
            var _power_c = _data.power_c;
            //_power_c = $.parseJSON(_power_c);
            var _power_ac = _data.power_ac;
           // _power_ac = $.parseJSON(_power_ac);
            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'power_sum') {
                       new_data.push(_power_sum);
                        options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_a') {
                       new_data.push(_power_a);
                        options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_b') {
                       new_data.push(_power_b);
                        options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_c') {
                       new_data.push(_power_c);
                        options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_ac') {
                       new_data.push(_power_ac);
                        options_power.legend.labels.push(this.value);
                   }

                   options_power.axes.xaxis.min = _power_sum[0][0];
                   options_power.axes.xaxis.max = _power_sum[_power_sum.length-1][0];
              });

                   if (plot_power) {
                        plot_power.destroy();
                    }


                  plot2_power = $.jqplot('chart100', new_data ,options_power);
                  plot2_power.themeEngine.newTheme('uma', temp);
                  plot2_power.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_power").attr('disabled','disabled');
              $("#stop_auto_update_power").removeAttr('disabled');
        }


        function do_update_power() {
            var values = {
		        "mac": mac,
                "data_req": "power"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/pmtr_smap_update_power/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {

					  console.log ("testing");
					  console.log (data);
                      update_plot_power(data);

				  },
				  error: function(data) {

                      clearTimeout(timeOut_power);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_power = setTimeout(do_update_power, 30000);
			//},5000);
	}

    	  //Auto update the chart
	  $('#auto_update_power').click( function(evt){
          evt.preventDefault();
	      do_update_power();
	   });

      $('#stop_auto_update_power').click(function(){
          clearTimeout(timeOut_power);
          $('#stop_auto_update_power').attr('disabled', 'disabled');
          $('#auto_update_power').removeAttr('disabled');
      });

        $('#stack_chart_power').click( function(evt){
            evt.preventDefault();
	        stackCharts_power();
	   });

	  function stackCharts_power(){
        if (timeOut_power) {
          clearTimeout(timeOut_power);
          $('#stop_auto_update_power').attr('disabled', 'disabled');
          $('#auto_update_power').removeAttr('disabled');
        }
        options_power.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){

                   if (this.id == 'power_sum') {
                       new_data.push(_power_sum);
                       options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_a') {
                       new_data.push(_power_a);
                       options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_b') {
                       new_data.push(_power_b);
                       options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_c') {
                       new_data.push(_power_c);
                       options_power.legend.labels.push(this.value);
                   } else if (this.id == 'power_ac') {
                       new_data.push(_power_ac);
                       options_power.legend.labels.push(this.value);
                   }

                   options_power.axes.xaxis.min = _power_sum[0][0];
                   options_power.axes.xaxis.max = _power_sum[_power_sum.length-1][0];
              });


                   if (plot_power) {
                        plot_power.destroy();
                    }


                  plot2_power = $.jqplot('chart100', new_data ,options_power);
                  plot2_power.themeEngine.newTheme('uma', temp);
                  plot2_power.activateTheme('uma');



      }




$("#get_stat").click(function(evt) {
        evt.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        get_statistics(from_date, to_date);

    });

    function get_statistics(from_date, to_date) {
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/charts/'+mac+'/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {



                      if (data.power.length == 0) {
                          $('.bottom-right').notify({
					  	    message: { text: 'No data found for the selected time period.'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
                      } else {
                          update_plot_power(data);
                          $("#auto_update_power").removeAttr('disabled');
                          $("#stop_auto_update_power").attr('disabled', 'disabled');

                      }

				  },
				  error: function(data) {


                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'+data},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });


    }

     $("#export_data").click(function(evt) {
        evt.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        export_to_spreadsheet(from_date, to_date);

    });


  function export_to_spreadsheet(from_date, to_date) {
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
            $.ajax({
              url : 'charts/download_sheet/'+mac+'/',
              type: 'POST',
              data: jsonText,
              dataType: 'json',
              contentType: "application/json; charset=utf-8",

              success : function(data) {
                  if (data.length == 0) {
                      $('.bottom-right').notify({
                        message: { text: 'No data found for the selected time period.'},
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                  } else {
                      JSONToCSVConvertor(data, mac, true);

                  }
              },
              error: function(data) {
                  $('.bottom-right').notify({
                        message: { text: 'Communication Error. Try again later!'+data},
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                      }).show();
              }
             });
    }


    function JSONToCSVConvertor(JSONData, ReportTitle, ShowLabel) {
        //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
        var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
        var CSV = '';
        //This condition will generate the Label/Header
        if (ShowLabel) {
            var row = "";
            //This loop will extract the label from 1st index of on array
            for (var index in arrData[0]) {
                //Now convert each value to string and comma-seprated
                row += index + ',';
            }
            row = row.slice(0, -1);
            //append Label row with line break
            CSV += row + '\r\n';
        }
        //1st loop is to extract each row
        for (var i = 0; i < arrData.length; i++) {
            var row = "";
            //2nd loop will extract each column and convert it in string comma-seprated
            for (var index in arrData[i]) {
                row += '"' + arrData[i][index] + '",';
            }
            row.slice(0, row.length - 1);
            //add a line break after each row
            CSV += row + '\r\n';
        }
        if (CSV == '') {
            alert("Invalid data");
            return;
        }
        //Generate a file name
        var fileName = "timeseries_";
        //this will remove the blank-spaces from the title and replace it with an underscore
        fileName += ReportTitle.replace(/ /g,"_");
        //Initialize file format you want csv or xls
        var uri = 'data:text/csv;charset=utf-8,' + escape(CSV);
        //this trick will generate a temp <a /> tag
        var link = document.createElement("a");
        link.href = uri;
        //set the visibility hidden so it will not effect on your web-layout
        link.style = "visibility:hidden";
        link.download = fileName + ".csv";
        //this part will append the anchor tag and remove it after automatic click
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

});