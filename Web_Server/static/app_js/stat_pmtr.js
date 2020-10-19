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
			      labels:["Power Phase A", "Power Phase B", "Power Phase C", "Power Sum"]
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
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
      var data_points_power = [_power_a, _power_b, _power_c, _power_sum];
	  var plot_power = $.jqplot('chart100', data_points_power ,options_power);
      $("#power_sum").attr('checked','checked');
      $("#power_a").attr('checked','checked');
      $("#power_b").attr('checked','checked');
      $("#power_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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
            var _power_sum = _data.power_sum;
            var _power_a = _data.power_a;
            var _power_b = _data.power_b;
            var _power_c = _data.power_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   //new_data.push(outdoor_temp);
                   if (this.id == 'power_sum') {
                       new_data.push(_power_sum);
                   } else if (this.id == 'power_a') {
                       new_data.push(_power_a);
                   } else if (this.id == 'power_b') {
                       new_data.push(_power_b);
                   } else if (this.id == 'power_c') {
                       new_data.push(_power_c);
                   } else if (this.id == 'power_sum') {
                       new_data.push(_power_sum);
                   }
                   options_power.legend.labels.push(this.value);
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
		        "device_info": device_info,
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
                   } else if (this.id == 'power_a') {
                       new_data.push(_power_a);
                   } else if (this.id == 'power_b') {
                       new_data.push(_power_b);
                   } else if (this.id == 'power_c') {
                       new_data.push(_power_c);
                   } else if (this.id == 'power_sum') {
                       new_data.push(_power_sum);
                   }
                   options_power.legend.labels.push(this.value);
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

    /**
     * Plot functions and values for Voltage
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */

	  //Plot options
	  var options_voltage = {
			    legend: {
			      show: true,
			      labels:["Voltage Phase A", "Voltage Phase B", "Voltage Phase C", "Voltage Average"]
			    },
                series:[{
                    label: 'Voltage (Volts)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _voltage_avg[0][0],
		            max: _voltage_avg[_voltage_avg.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Voltage (Volts)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_voltage = [_voltage_a, _voltage_b, _voltage_c, _voltage_avg];
	  var plot_voltage = $.jqplot('chart101', data_points_voltage ,options_voltage);
      $("#voltage_avg").attr('checked','checked');
      $("#voltage_a").attr('checked','checked');
      $("#voltage_b").attr('checked','checked');
      $("#voltage_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_voltage.themeEngine.newTheme('uma', temp);
        plot_voltage.activateTheme('uma');

        var timeOut_voltage;

        function update_plot_voltage(_data) {
            var _voltage_avg = _data.voltage_avg;
            var _voltage_a = _data.voltage_a;
            var _voltage_b = _data.voltage_b;
            var _voltage_c = _data.voltage_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'voltage_avg') {
                       new_data.push(_voltage_avg);
                   } else if (this.id == 'voltage_a') {
                       new_data.push(_voltage_a);
                   } else if (this.id == 'voltage_b') {
                       new_data.push(_voltage_b);
                   } else if (this.id == 'voltage_c') {
                       new_data.push(_voltage_c);
                   }
                   options_voltage.legend.labels.push(this.value);
                   options_voltage.axes.xaxis.min = _voltage_avg[0][0];
                   options_voltage.axes.xaxis.max = _voltage_avg[_voltage_avg.length-1][0];
              });

                   if (plot_voltage) {
                        plot_voltage.destroy();
                    }

                  plot2_voltage = $.jqplot('chart101', new_data ,options_voltage);
                  plot2_voltage.themeEngine.newTheme('uma', temp);
                  plot2_voltage.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_voltage").attr('disabled','disabled');
              $("#stop_auto_update_voltage").removeAttr('disabled');
        }


        function do_update_voltage() {
            var values = {
		        "device_info": device_info,
                "data_req": "voltage"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_voltage/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_voltage(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_voltage);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_voltage = setTimeout(do_update_voltage, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_voltage').click( function(evt){
          evt.preventDefault();
	      do_update_voltage();
	   });

      $('#stop_auto_update_voltage').click(function(){
          clearTimeout(timeOut_voltage);
          $('#stop_auto_update_voltage').attr('disabled', 'disabled');
          $('#auto_update_voltage').removeAttr('disabled');
      });

        $('#stack_chart_voltage').click( function(evt){
            evt.preventDefault();
	        stackCharts_voltage();
	   });

	  function stackCharts_voltage(){
        if (timeOut_voltage) {
          clearTimeout(timeOut_voltage);
          $('#stop_auto_update_voltage').attr('disabled', 'disabled');
          $('#auto_update_voltage').removeAttr('disabled');
        }
        options_voltage.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'voltage_avg') {
                       new_data.push(_voltage_avg);
                   } else if (this.id == 'voltage_a') {
                       new_data.push(_voltage_a);
                   } else if (this.id == 'voltage_b') {
                       new_data.push(_voltage_b);
                   } else if (this.id == 'voltage_c') {
                       new_data.push(_voltage_c);
                   }
                   options_voltage.legend.labels.push(this.value);
                   options_voltage.axes.xaxis.min = _voltage_avg[0][0];
                   options_voltage.axes.xaxis.max = _voltage_avg[_voltage_avg.length-1][0];
              });


                   if (plot_voltage) {
                        plot_voltage.destroy();
                    }

                  plot2_voltage = $.jqplot('chart101', new_data ,options_voltage);
                  plot2_voltage.themeEngine.newTheme('uma', temp);
                  plot2_voltage.activateTheme('uma');



      }

    /**
     * Plot functions and values for Current
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */

	  //Plot options
	  var options_current = {
			    legend: {
			      show: true,
			      labels:["Current Phase A", "Current Phase B", "Current Phase C"]
			    },
                series:[{
                    label: 'Current (A)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _current_a[0][0],
		            max: _current_a[_current_a.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Current (A)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_current = [_current_a, _current_b, _current_c];
	  var plot_current = $.jqplot('chart102', data_points_current ,options_current);
      $("#current_a").attr('checked','checked');
      $("#current_b").attr('checked','checked');
      $("#current_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_current.themeEngine.newTheme('uma', temp);
        plot_current.activateTheme('uma');

        var timeOut_current;

        function update_plot_current(_data) {
            var _current_a = _data.current_a;
            var _current_b = _data.current_b;
            var _current_c = _data.current_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'current_a') {
                       new_data.push(_current_a);
                   } else if (this.id == 'current_b') {
                       new_data.push(_current_b);
                   } else if (this.id == 'current_c') {
                       new_data.push(_current_c);
                   }
                   options_current.legend.labels.push(this.value);
                   options_current.axes.xaxis.min = _current_a[0][0];
                   options_current.axes.xaxis.max = _current_a[_current_a.length-1][0];
              });

                   if (plot_current) {
                        plot_current.destroy();
                    }

                  plot2_current = $.jqplot('chart102', new_data ,options_current);
                  plot2_current.themeEngine.newTheme('uma', temp);
                  plot2_current.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_current").attr('disabled','disabled');
              $("#stop_auto_update_current").removeAttr('disabled');
        }


        function do_update_current() {
            var values = {
		        "device_info": device_info,
                "data_req": "current"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_current/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_current(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_current);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_current = setTimeout(do_update_current, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_current').click( function(evt){
          evt.preventDefault();
	      do_update_current();
	   });

      $('#stop_auto_update_current').click(function(){
          clearTimeout(timeOut_current);
          $('#stop_auto_update_current').attr('disabled', 'disabled');
          $('#auto_update_current').removeAttr('disabled');
      });

        $('#stack_chart_current').click( function(evt){
            evt.preventDefault();
	        stackCharts_current();
	   });

	  function stackCharts_current(){
        if (timeOut_current) {
          clearTimeout(timeOut_current);
          $('#stop_auto_update_current').attr('disabled', 'disabled');
          $('#auto_update_current').removeAttr('disabled');
        }
        options_current.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'current_a') {
                       new_data.push(_current_a);
                   } else if (this.id == 'current_b') {
                       new_data.push(_current_b);
                   } else if (this.id == 'current_c') {
                       new_data.push(_current_c);
                   }
                   options_current.legend.labels.push(this.value);
                   options_current.axes.xaxis.min = _current_a[0][0];
                   options_current.axes.xaxis.max = _current_a[_current_a.length-1][0];
              });


                   if (plot_current) {
                        plot_current.destroy();
                    }

                  plot2_current = $.jqplot('chart102', new_data ,options_current);
                  plot2_current.themeEngine.newTheme('uma', temp);
                  plot2_current.activateTheme('uma');

      }


    /**
     * Plot functions and values for Power Factor
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_pf = {
			    legend: {
			      show: true,
			      labels:["Power Factor Phase A", "Power Factor Phase B", "Power Factor Phase C", "Power Factor Average"]
			    },
                series:[{
                    label: 'Power Factor',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _pf_avg[0][0],
		            max: _pf_avg[_pf_avg.length-1][0]
			      },
			      yaxis: {
			        min:0,
			        max:1,
			        label: "Power Factor"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pf = [_pf_a, _pf_b, _pf_c, _pf_avg];
	  var plot_pf = $.jqplot('chart103', data_points_pf ,options_pf);
      $("#pf_avg").attr('checked','checked');
      $("#pf_a").attr('checked','checked');
      $("#pf_b").attr('checked','checked');
      $("#pf_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_pf.themeEngine.newTheme('uma', temp);
        plot_pf.activateTheme('uma');

        var timeOut_pf;

        function update_plot_pf(_data) {
            var _pf_avg = _data.power_factor_avg;
            var _pf_a = _data.power_factor_a;
            var _pf_b = _data.power_factor_b;
            var _pf_c = _data.power_factor_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   //new_data.push(outdoor_temp);
                   if (this.id == 'pf_avg') {
                       new_data.push(_pf_avg);
                   } else if (this.id == 'pf_a') {
                       new_data.push(_pf_a);
                   } else if (this.id == 'pf_b') {
                       new_data.push(_pf_b);
                   } else if (this.id == 'pf_c') {
                       new_data.push(_pf_c);
                   }
                   options_pf.legend.labels.push(this.value);
                   options_pf.axes.xaxis.min = _pf_avg[0][0];
                   options_pf.axes.xaxis.max = _pf_avg[_pf_avg.length-1][0];
              });

                   if (plot_pf) {
                        plot_pf.destroy();
                    }

                  plot2_pf = $.jqplot('chart103', new_data ,options_pf);
                  plot2_pf.themeEngine.newTheme('uma', temp);
                  plot2_pf.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pf").attr('disabled','disabled');
              $("#stop_auto_update_pf").removeAttr('disabled');
        }


        function do_update_pf() {
            var values = {
		        "device_info": device_info,
                "data_req": "power_factor"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_pf/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_pf(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_pf);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_pf = setTimeout(do_update_pf, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_pf').click( function(evt){
          evt.preventDefault();
	      do_update_pf();
	   });

      $('#stop_auto_update_pf').click(function(){
          clearTimeout(timeOut_pf);
          $('#stop_auto_update_pf').attr('disabled', 'disabled');
          $('#auto_update_pf').removeAttr('disabled');
      });

        $('#stack_chart_pf').click( function(evt){
            evt.preventDefault();
	        stackCharts_pf();
	   });

	  function stackCharts_pf(){
        if (timeOut_pf) {
          clearTimeout(timeOut_pf);
          $('#stop_auto_update_pf').attr('disabled', 'disabled');
          $('#auto_update_pf').removeAttr('disabled');
        }
        options_pf.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'pf_avg') {
                       new_data.push(_pf_avg);
                   } else if (this.id == 'pf_a') {
                       new_data.push(_pf_a);
                   } else if (this.id == 'pf_b') {
                       new_data.push(_pf_b);
                   } else if (this.id == 'pf_c') {
                       new_data.push(_pf_c);
                   }
                   options_pf.legend.labels.push(this.value);
                   options_pf.axes.xaxis.min = _power_factor_avg[0][0];
                   options_pf.axes.xaxis.max = _power_factor_avg[_power_factor_avg.length-1][0];
              });


                   if (plot_pf) {
                        plot_pf.destroy();
                    }

                  plot2_pf = $.jqplot('chart103', new_data ,options_pf);
                  plot2_pf.themeEngine.newTheme('uma', temp);
                  plot2_pf.activateTheme('uma');

      }


    /**
     * Plot functions and values for Frequency
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_frequency = {
			    legend: {
			      show: true,
			      labels:["Frequency"]
			    },
                series:[{
                    label: 'Frequency (Hz)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _frequency[0][0],
		            max: _frequency[_frequency.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Frequency"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_freq = [_frequency];
	  var plot_frequency = $.jqplot('chart104', data_points_freq ,options_frequency);
      $("#frequency").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_frequency.themeEngine.newTheme('uma', temp);
        plot_frequency.activateTheme('uma');

        var timeOut_frequency;

        function update_plot_frequency(_data) {
            var _frequency = _data.frequency;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'frequency') {
                       new_data.push(_frequency);
                   }
                   options_frequency.legend.labels.push(this.value);
                   options_frequency.axes.xaxis.min = _frequency[0][0];
                   options_frequency.axes.xaxis.max = _frequency[_frequency.length-1][0];
              });

                   if (plot_frequency) {
                        plot_frequency.destroy();
                    }

                  plot2_frequency = $.jqplot('chart104', new_data ,options_frequency);
                  plot2_frequency.themeEngine.newTheme('uma', temp);
                  plot2_frequency.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_frequency").attr('disabled','disabled');
              $("#stop_auto_update_frequency").removeAttr('disabled');
        }


        function do_update_frequency() {
            var values = {
		        "device_info": device_info,
                "data_req": "frequency"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_frequency/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_frequency(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_frequency);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_frequency = setTimeout(do_update_frequency, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_frequency').click( function(evt){
          evt.preventDefault();
	      do_update_frequency();
	   });

      $('#stop_auto_update_frequency').click(function(){
          clearTimeout(timeOut_frequency);
          $('#stop_auto_update_frequency').attr('disabled', 'disabled');
          $('#auto_update_frequency').removeAttr('disabled');
      });

        $('#stack_chart_frequency').click( function(evt){
            evt.preventDefault();
	        stackCharts_frequency();
	   });

	  function stackCharts_frequency(){
        if (timeOut_frequency) {
          clearTimeout(timeOut_frequency);
          $('#stop_auto_update_frequency').attr('disabled', 'disabled');
          $('#auto_update_frequency').removeAttr('disabled');
        }
        options_frequency.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'frequency') {
                       new_data.push(_frequency);
                   }
                   options_frequency.legend.labels.push(this.value);
                   options_frequency.axes.xaxis.min = _frequency[0][0];
                   options_frequency.axes.xaxis.max = _frequency[_frequency.length-1][0];
              });


                   if (plot_frequency) {
                        plot_frequency.destroy();
                    }

                  plot2_frequency = $.jqplot('chart104', new_data ,options_frequency);
                  plot2_frequency.themeEngine.newTheme('uma', temp);
                  plot2_frequency.activateTheme('uma');

      }




    /**
     * Plot functions and values for Power Apparent
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_pa = {
			    legend: {
			      show: true,
			      labels:["Power Apparent Phase A", "Power Apparent Phase B", "Power Apparent Phase C", "Power Apparent Sum"]
			    },
                series:[{
                    label: 'Power Apparent (kVA)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _pa_sum[0][0],
		            max: _pa_sum[_pa_sum.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Power Apparent (kVA)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pa = [_pa_a, _pa_b, _pa_c, _pa_sum];
	  var plot_pa = $.jqplot('chart105', data_points_pa ,options_pa);
      $("#pa_sum").attr('checked','checked');
      $("#pa_a").attr('checked','checked');
      $("#pa_b").attr('checked','checked');
      $("#pa_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_pa.themeEngine.newTheme('uma', temp);
        plot_pa.activateTheme('uma');

        var timeOut_pa;

        function update_plot_pa(_data) {
            var _pa_sum = _data.power_apparent_sum;
            var _pa_a = _data.power_apparent_a;
            var _pa_b = _data.power_apparent_b;
            var _pa_c = _data.power_apparent_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'pa_sum') {
                       new_data.push(_pa_sum);
                   } else if (this.id == 'pa_a') {
                       new_data.push(_pa_a);
                   } else if (this.id == 'pa_b') {
                       new_data.push(_pa_b);
                   } else if (this.id == 'pa_c') {
                       new_data.push(_pa_c);
                   }
                   options_pa.legend.labels.push(this.value);
                   options_pa.axes.xaxis.min = _pa_sum[0][0];
                   options_pa.axes.xaxis.max = _pa_sum[_pa_sum.length-1][0];
              });

                   if (plot_pa) {
                        plot_pa.destroy();
                    }

                  plot2_pa = $.jqplot('chart105', new_data ,options_pa);
                  plot2_pa.themeEngine.newTheme('uma', temp);
                  plot2_pa.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pa").attr('disabled','disabled');
              $("#stop_auto_update_pa").removeAttr('disabled');
        }


        function do_update_pa() {
            var values = {
		        "device_info": device_info,
                "data_req": "power_apparent"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_pa/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_pa(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_pa);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_pa = setTimeout(do_update_pa, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_pa').click( function(evt){
          evt.preventDefault();
	      do_update_pa();
	   });

      $('#stop_auto_update_pa').click(function(){
          clearTimeout(timeOut_pa);
          $('#stop_auto_update_pa').attr('disabled', 'disabled');
          $('#auto_update_pa').removeAttr('disabled');
      });

        $('#stack_chart_pa').click( function(evt){
            evt.preventDefault();
	        stackCharts_pa();
	   });

	  function stackCharts_pa(){
        if (timeOut_pa) {
          clearTimeout(timeOut_pa);
          $('#stop_auto_update_pa').attr('disabled', 'disabled');
          $('#auto_update_pa').removeAttr('disabled');
        }
        options_pa.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'pa_sum') {
                       new_data.push(_pa_sum);
                   } else if (this.id == 'pa_a') {
                       new_data.push(_pa_a);
                   } else if (this.id == 'pa_b') {
                       new_data.push(_pa_b);
                   } else if (this.id == 'pa_c') {
                       new_data.push(_pa_c);
                   }
                   options_pa.legend.labels.push(this.value);
                   options_pa.axes.xaxis.min = _pa_sum[0][0];
                   options_pa.axes.xaxis.max = _pa_sum[_pa_sum.length-1][0];
              });


                   if (plot_pa) {
                        plot_pa.destroy();
                    }

                  plot2_pa = $.jqplot('chart105', new_data ,options_pa);
                  plot2_pa.themeEngine.newTheme('uma', temp);
                  plot2_pa.activateTheme('uma');

      }


      /**
     * Plot functions and values for Power Reactive
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_pr = {
			    legend: {
			      show: true,
			      labels:["Power Reactive Phase A", "Power Reactive Phase B", "Power Reactive Phase C", "Power Reactive Sum"]
			    },
                series:[{
                    label: 'Power Reactive (kVAR)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _pr_sum[0][0],
		            max: _pr_sum[_pr_sum.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Power Reactive (kVAR)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pr = [_pr_a, _pr_b, _pr_c, _pr_sum];
	  var plot_pr = $.jqplot('chart106', data_points_pr ,options_pr);
      $("#pr_sum").attr('checked','checked');
      $("#pr_a").attr('checked','checked');
      $("#pr_b").attr('checked','checked');
      $("#pr_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_pr.themeEngine.newTheme('uma', temp);
        plot_pr.activateTheme('uma');

        var timeOut_pr;

        function update_plot_pr(_data) {
            var _pr_sum = _data.power_reactive_sum;
            var _pr_a = _data.power_reactive_a;
            var _pr_b = _data.power_reactive_b;
            var _pr_c = _data.power_reactive_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'pr_sum') {
                       new_data.push(_pr_sum);
                   } else if (this.id == 'pr_a') {
                       new_data.push(_pr_a);
                   } else if (this.id == 'pr_b') {
                       new_data.push(_pr_b);
                   } else if (this.id == 'pr_c') {
                       new_data.push(_pr_c);
                   }
                   options_pr.legend.labels.push(this.value);
                   options_pr.axes.xaxis.min = _pr_sum[0][0];
                   options_pr.axes.xaxis.max = _pr_sum[_pr_sum.length-1][0];
              });

                   if (plot_pr) {
                        plot_pr.destroy();
                    }

                  plot2_pr = $.jqplot('chart106', new_data ,options_pr);
                  plot2_pr.themeEngine.newTheme('uma', temp);
                  plot2_pr.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pr").attr('disabled','disabled');
              $("#stop_auto_update_pr").removeAttr('disabled');
        }


        function do_update_pr() {
            var values = {
		        "device_info": device_info,
                "data_req": "power_reactive"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_pr/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_pr(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_pr);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_pr = setTimeout(do_update_pr, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_pr').click( function(evt){
          evt.preventDefault();
	      do_update_pr();
	   });

      $('#stop_auto_update_pr').click(function(){
          clearTimeout(timeOut_pr);
          $('#stop_auto_update_pr').attr('disabled', 'disabled');
          $('#auto_update_pr').removeAttr('disabled');
      });

        $('#stack_chart_pr').click( function(evt){
            evt.preventDefault();
	        stackCharts_pr();
	   });

	  function stackCharts_pr(){
        if (timeOut_pr) {
          clearTimeout(timeOut_pr);
          $('#stop_auto_update_pr').attr('disabled', 'disabled');
          $('#auto_update_pr').removeAttr('disabled');
        }
        options_pr.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'pr_sum') {
                       new_data.push(_pr_sum);
                   } else if (this.id == 'pr_a') {
                       new_data.push(_pr_a);
                   } else if (this.id == 'pr_b') {
                       new_data.push(_pr_b);
                   } else if (this.id == 'pr_c') {
                       new_data.push(_pr_c);
                   }
                   options_pr.legend.labels.push(this.value);
                   options_pr.axes.xaxis.min = _pr_sum[0][0];
                   options_pr.axes.xaxis.max = _pr_sum[_pr_sum.length-1][0];
              });


                   if (plot_pr) {
                        plot_pr.destroy();
                    }

                  plot2_pr = $.jqplot('chart106', new_data ,options_pr);
                  plot2_pr.themeEngine.newTheme('uma', temp);
                  plot2_pr.activateTheme('uma');

      }


    /**
     * Plot functions and values for Energy Apparent
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_ea = {
			    legend: {
			      show: true,
			      labels:["Energy Apparent Phase A", "Energy Apparent Phase B", "Energy Apparent Phase C", "Energy Apparent Sum"]
			    },
                series:[{
                    label: 'Energy Apparent (kVAh)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _ea_sum[0][0],
		            max: _ea_sum[_ea_sum.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Energy Apparent (kVAh)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_ea = [_ea_a, _ea_b, _ea_c, _ea_sum];
	  var plot_ea = $.jqplot('chart107', data_points_ea ,options_ea);
      $("#ea_sum").attr('checked','checked');
      $("#ea_a").attr('checked','checked');
      $("#ea_b").attr('checked','checked');
      $("#ea_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_ea.themeEngine.newTheme('uma', temp);
        plot_ea.activateTheme('uma');

        var timeOut_ea;

        function update_plot_ea(_data) {
            var _ea_sum = _data.energy_apparent_sum;
            var _ea_a = _data.energy_apparent_a;
            var _ea_b = _data.energy_apparent_b;
            var _ea_c = _data.energy_apparent_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'ea_sum') {
                       new_data.push(_ea_sum);
                   } else if (this.id == 'ea_a') {
                       new_data.push(_ea_a);
                   } else if (this.id == 'ea_b') {
                       new_data.push(_ea_b);
                   } else if (this.id == 'ea_c') {
                       new_data.push(_ea_c);
                   }
                   options_ea.legend.labels.push(this.value);
                   options_ea.axes.xaxis.min = _ea_sum[0][0];
                   options_ea.axes.xaxis.max = _ea_sum[_ea_sum.length-1][0];
              });

                   if (plot_ea) {
                        plot_ea.destroy();
                    }

                  plot2_ea = $.jqplot('chart107', new_data ,options_ea);
                  plot2_ea.themeEngine.newTheme('uma', temp);
                  plot2_ea.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_ea").attr('disabled','disabled');
              $("#stop_auto_update_ea").removeAttr('disabled');
        }


        function do_update_ea() {
            var values = {
		        "device_info": device_info,
                "data_req": "energy_apparent"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_ea/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_ea(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_ea);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_ea = setTimeout(do_update_ea, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_ea').click( function(evt){
          evt.preventDefault();
	      do_update_ea();
	   });

      $('#stop_auto_update_ea').click(function(){
          clearTimeout(timeOut_ea);
          $('#stop_auto_update_ea').attr('disabled', 'disabled');
          $('#auto_update_ea').removeAttr('disabled');
      });

        $('#stack_chart_ea').click( function(evt){
            evt.preventDefault();
	        stackCharts_ea();
	   });

	  function stackCharts_ea(){
        if (timeOut_ea) {
          clearTimeout(timeOut_ea);
          $('#stop_auto_update_ea').attr('disabled', 'disabled');
          $('#auto_update_ea').removeAttr('disabled');
        }
        options_ea.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'ea_sum') {
                       new_data.push(_ea_sum);
                   } else if (this.id == 'ea_a') {
                       new_data.push(_ea_a);
                   } else if (this.id == 'ea_b') {
                       new_data.push(_ea_b);
                   } else if (this.id == 'ea_c') {
                       new_data.push(_ea_c);
                   }
                   options_ea.legend.labels.push(this.value);
                   options_ea.axes.xaxis.min = _ea_sum[0][0];
                   options_ea.axes.xaxis.max = _ea_sum[_ea_sum.length-1][0];
              });


                   if (plot_ea) {
                        plot_ea.destroy();
                    }

                  plot2_ea = $.jqplot('chart107', new_data ,options_ea);
                  plot2_ea.themeEngine.newTheme('uma', temp);
                  plot2_ea.activateTheme('uma');

      }


    /**
     * Plot functions and values for Energy Reactive
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_er = {
			    legend: {
			      show: true,
			      labels:["Energy Reactive Phase A", "Energy Reactive Phase B", "Energy Reactive Phase C", "Energy Reactive Sum"]
			    },
                series:[{
                    label: 'Energy Reactive (kVARh)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _er_sum[0][0],
		            max: _er_sum[_er_sum.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Energy Reactive (kVARh)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_er = [_er_a, _er_b, _er_c, _er_sum];
	  var plot_er = $.jqplot('chart108', data_points_er ,options_er);
      $("#er_sum").attr('checked','checked');
      $("#er_a").attr('checked','checked');
      $("#er_b").attr('checked','checked');
      $("#er_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_er.themeEngine.newTheme('uma', temp);
        plot_er.activateTheme('uma');

        var timeOut_er;

        function update_plot_er(_data) {
            var _er_sum = _data.energy_reactive_sum;
            var _er_a = _data.energy_reactive_a;
            var _er_b = _data.energy_reactive_b;
            var _er_c = _data.energy_reactive_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'er_sum') {
                       new_data.push(_er_sum);
                   } else if (this.id == 'er_a') {
                       new_data.push(_er_a);
                   } else if (this.id == 'er_b') {
                       new_data.push(_er_b);
                   } else if (this.id == 'er_c') {
                       new_data.push(_er_c);
                   }
                   options_er.legend.labels.push(this.value);
                   options_er.axes.xaxis.min = _er_sum[0][0];
                   options_er.axes.xaxis.max = _er_sum[_er_sum.length-1][0];
              });

                   if (plot_er) {
                        plot_er.destroy();
                    }

                  plot2_er = $.jqplot('chart108', new_data ,options_er);
                  plot2_er.themeEngine.newTheme('uma', temp);
                  plot2_er.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_er").attr('disabled','disabled');
              $("#stop_auto_update_er").removeAttr('disabled');
        }


        function do_update_er() {
            var values = {
		        "device_info": device_info,
                "data_req": "energy_reactive"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_er/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_er(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_er);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_er = setTimeout(do_update_er, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_er').click( function(evt){
          evt.preventDefault();
	      do_update_er();
	   });

      $('#stop_auto_update_er').click(function(){
          clearTimeout(timeOut_er);
          $('#stop_auto_update_er').attr('disabled', 'disabled');
          $('#auto_update_er').removeAttr('disabled');
      });

        $('#stack_chart_er').click( function(evt){
            evt.preventDefault();
	        stackCharts_er();
	   });

	  function stackCharts_er(){
        if (timeOut_er) {
          clearTimeout(timeOut_er);
          $('#stop_auto_update_er').attr('disabled', 'disabled');
          $('#auto_update_er').removeAttr('disabled');
        }
        options_er.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'er_sum') {
                       new_data.push(_er_sum);
                   } else if (this.id == 'er_a') {
                       new_data.push(_er_a);
                   } else if (this.id == 'er_b') {
                       new_data.push(_er_b);
                   } else if (this.id == 'er_c') {
                       new_data.push(_er_c);
                   }
                   options_er.legend.labels.push(this.value);
                   options_er.axes.xaxis.min = _er_sum[0][0];
                   options_er.axes.xaxis.max = _er_sum[_er_sum.length-1][0];
              });


                   if (plot_ea) {
                        plot_ea.destroy();
                    }

                  plot2_er = $.jqplot('chart108', new_data ,options_er);
                  plot2_er.themeEngine.newTheme('uma', temp);
                  plot2_er.activateTheme('uma');

      }

      /**
     * Plot functions and values for Energy Net
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_e_net = {
			    legend: {
			      show: true,
			      labels:["Energy Net Phase A", "Energy Net Phase B", "Energy Net Phase C", "Energy Net Sum", "Energy Net Sum NR"]
			    },
                series:[{
                    label: 'Energy Net (kWh)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _e_sum_nr[0][0],
		            max: _e_sum_nr[_e_sum_nr.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Energy Net (kWh)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_e_net = [_e_a_net, _e_b_net, _e_c_net, _e_sum, _e_sum_nr];
	  var plot_e_net = $.jqplot('chart109', data_points_e_net ,options_e_net);
      $("#e_sum").attr('checked','checked');
         $("#e_sum_nr").attr('checked','checked');
      $("#e_a_net").attr('checked','checked');
      $("#e_b_net").attr('checked','checked');
      $("#e_c_net").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_e_net.themeEngine.newTheme('uma', temp);
        plot_e_net.activateTheme('uma');

        var timeOut_e_net;

        function update_plot_e_net(_data) {
            var _e_sum = _data.energy_sum;
            var _e_sum_nr = _data.energy_sum_nr;
            var _e_a_net = _data.energy_a_net;
            var _e_b_net = _data.energy_b_net;
            var _e_c_net = _data.energy_c_net;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'e_sum') {
                       new_data.push(_e_sum);
                   } else if (this.id == 'e_sum_nr') {
                       new_data.push(_e_sum_nr);
                   } else if (this.id == 'e_a_net') {
                       new_data.push(_e_a_net);
                   } else if (this.id == 'e_b_net') {
                       new_data.push(_e_b_net);
                   } else if (this.id == 'e_c_net') {
                       new_data.push(_e_c_net);
                   }
                   options_e_net.legend.labels.push(this.value);
                   options_e_net.axes.xaxis.min = _e_sum_nr[0][0];
                   options_e_net.axes.xaxis.max = _e_sum_nr[_e_sum_nr.length-1][0];
              });

                   if (plot_e_net) {
                        plot_e_net.destroy();
                    }

                  plot2_e_net = $.jqplot('chart109', new_data ,options_e_net);
                  plot2_e_net.themeEngine.newTheme('uma', temp);
                  plot2_e_net.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_e_net").attr('disabled','disabled');
              $("#stop_auto_update_e_net").removeAttr('disabled');
        }


        function do_update_e_net() {
            var values = {
		        "device_info": device_info,
                "data_req": "energy_net"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_e_net/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_e_net(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_e_net);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_e_net = setTimeout(do_update_e_net, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_e_net').click( function(evt){
          evt.preventDefault();
	      do_update_e_net();
	   });

      $('#stop_auto_update_e_net').click(function(){
          clearTimeout(timeOut_e_net);
          $('#stop_auto_update_e_net').attr('disabled', 'disabled');
          $('#auto_update_e_net').removeAttr('disabled');
      });

        $('#stack_chart_e_net').click( function(evt){
            evt.preventDefault();
	        stackCharts_e_net();
	   });

	  function stackCharts_e_net(){
        if (timeOut_e_net) {
          clearTimeout(timeOut_e_net);
          $('#stop_auto_update_e_net').attr('disabled', 'disabled');
          $('#auto_update_e_net').removeAttr('disabled');
        }
        options_e_net.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'e_sum') {
                       new_data.push(_e_sum);
                   } else if (this.id == 'e_sum_nr') {
                       new_data.push(_e_sum_nr);
                   } else if (this.id == 'e_a_net') {
                       new_data.push(_e_a_net);
                   } else if (this.id == 'e_b_net') {
                       new_data.push(_e_b_net);
                   } else if (this.id == 'e_c_net') {
                       new_data.push(_e_c_net);
                   }
                   options_e_net.legend.labels.push(this.value);
                   options_e_net.axes.xaxis.min = _e_sum_nr[0][0];
                   options_e_net.axes.xaxis.max = _e_sum_nr[_e_sum_nr.length-1][0];
              });


                   if (plot_e_net) {
                        plot_e_net.destroy();
                    }

                  plot2_e_net = $.jqplot('chart109', new_data ,options_e_net);
                  plot2_e_net.themeEngine.newTheme('uma', temp);
                  plot2_e_net.activateTheme('uma');

      }


          /**
     * Plot functions and values for Energy Positive
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_epos = {
			    legend: {
			      show: true,
			      labels:["Energy Positive Phase A", "Energy Positive Phase B", "Energy Positive Phase C", "Energy Positive Sum", "Energy Positive Sum NR"]
			    },
                series:[{
                    label: 'Energy Positive (kWh)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _epos_sum_nr[0][0],
		            max: _epos_sum_nr[_epos_sum_nr.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Energy Positive (kWh)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_epos = [_epos_a, _epos_b, _epos_c, _epos_sum, _epos_sum_nr];
	  var plot_epos = $.jqplot('chart110', data_points_epos ,options_epos);
      $("#epos_sum").attr('checked','checked');
         $("#epos_sum_nr").attr('checked','checked');
      $("#epos_a").attr('checked','checked');
      $("#epos_b").attr('checked','checked');
      $("#epos_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_epos.themeEngine.newTheme('uma', temp);
        plot_epos.activateTheme('uma');

        var timeOut_epos;

        function update_plot_epos(_data) {
            var _epos_sum = _data.energy_pos_sum;
            var _epos_sum_nr = _data.energy_pos_sum_nr;
            var _epos_a = _data.energy_pos_a;
            var _epos_b = _data.energy_pos_b;
            var _epos_c = _data.energy_pos_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'epos_sum') {
                       new_data.push(_epos_sum);
                   } else if (this.id == 'epos_sum_nr') {
                       new_data.push(_epos_sum_nr);
                   } else if (this.id == 'epos_a') {
                       new_data.push(_epos_a);
                   } else if (this.id == 'epos_b') {
                       new_data.push(_epos_b);
                   } else if (this.id == 'epos_c') {
                       new_data.push(_epos_c);
                   }
                   options_epos.legend.labels.push(this.value);
                   options_epos.axes.xaxis.min = _epos_sum_nr[0][0];
                   options_epos.axes.xaxis.max = _epos_sum_nr[_epos_sum_nr.length-1][0];
              });

                   if (plot_epos) {
                        plot_epos.destroy();
                    }

                  plot2_epos = $.jqplot('chart110', new_data ,options_epos);
                  plot2_epos.themeEngine.newTheme('uma', temp);
                  plot2_epos.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_epos").attr('disabled','disabled');
              $("#stop_auto_update_epos").removeAttr('disabled');
        }


        function do_update_epos() {
            var values = {
		        "device_info": device_info,
                "data_req": "energy_pos"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_epos/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_epos(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_epos);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_epos = setTimeout(do_update_epos, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_epos').click( function(evt){
          evt.preventDefault();
	      do_update_epos();
	   });

      $('#stop_auto_update_epos').click(function(){
          clearTimeout(timeOut_epos);
          $('#stop_auto_update_epos').attr('disabled', 'disabled');
          $('#auto_update_epos').removeAttr('disabled');
      });

        $('#stack_chart_epos').click( function(evt){
            evt.preventDefault();
	        stackCharts_epos();
	   });

	  function stackCharts_epos(){
        if (timeOut_epos) {
          clearTimeout(timeOut_epos);
          $('#stop_auto_update_epos').attr('disabled', 'disabled');
          $('#auto_update_epos').removeAttr('disabled');
        }
        options_epos.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'epos_sum') {
                       new_data.push(_epos_sum);
                   } else if (this.id == 'epos_sum_nr') {
                       new_data.push(_epos_sum_nr);
                   } else if (this.id == 'epos_a') {
                       new_data.push(_epos_a);
                   } else if (this.id == 'epos_b') {
                       new_data.push(_epos_b);
                   } else if (this.id == 'epos_c') {
                       new_data.push(_epos_c);
                   }
                   options_epos.legend.labels.push(this.value);
                   options_epos.axes.xaxis.min = _epos_sum_nr[0][0];
                   options_epos.axes.xaxis.max = _epos_sum_nr[_epos_sum_nr.length-1][0];
              });


                   if (plot_epos) {
                        plot_epos.destroy();
                    }

                  plot2_epos = $.jqplot('chart110', new_data ,options_epos);
                  plot2_epos.themeEngine.newTheme('uma', temp);
                  plot2_epos.activateTheme('uma');

      }

    /**
     * Plot functions and values for Energy Negative
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
	  var options_eneg = {
			    legend: {
			      show: true,
			      labels:["Energy Negative Phase A", "Energy Negative Phase B", "Energy Negative Phase C", "Energy Negative Sum", "Energy Negative Sum NR"]
			    },
                series:[{
                    label: 'Energy Negative (kWh)',
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
			        tickOptions:{formatString:'%I:%M:%S %p'},
			        numberTicks: 10,
		            min : _eneg_sum_nr[0][0],
		            max: _eneg_sum_nr[_epos_sum_nr.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Energy Negative (kWh)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_eneg = [_eneg_a, _eneg_b, _eneg_c, _eneg_sum, _eneg_sum_nr];
	  var plot_eneg = $.jqplot('chart111', data_points_eneg ,options_eneg);
      $("#eneg_sum").attr('checked','checked');
         $("#eneg_sum_nr").attr('checked','checked');
      $("#eneg_a").attr('checked','checked');
      $("#eneg_b").attr('checked','checked');
      $("#eneg_c").attr('checked','checked');

      temp = {
            seriesStyles: {
                seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
            },
            grid: {
                //backgroundColor: 'rgb(211, 233, 195)'
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


        plot_eneg.themeEngine.newTheme('uma', temp);
        plot_eneg.activateTheme('uma');

        var timeOut_eneg;

        function update_plot_eneg(_data) {
            var _eneg_sum = _data.energy_neg_sum;
            var _eneg_sum_nr = _data.energy_neg_sum_nr;
            var _eneg_a = _data.energy_neg_a;
            var _eneg_b = _data.energy_neg_b;
            var _eneg_c = _data.energy_neg_c;
            var new_data = [];

              $.each($('input:checked'), function(index, value){
                   if (this.id == 'eneg_sum') {
                       new_data.push(_eneg_sum);
                   } else if (this.id == 'eneg_sum_nr') {
                       new_data.push(_eneg_sum_nr);
                   } else if (this.id == 'eneg_a') {
                       new_data.push(_eneg_a);
                   } else if (this.id == 'eneg_b') {
                       new_data.push(_eneg_b);
                   } else if (this.id == 'eneg_c') {
                       new_data.push(_eneg_c);
                   }
                   options_eneg.legend.labels.push(this.value);
                   options_eneg.axes.xaxis.min = _eneg_sum_nr[0][0];
                   options_eneg.axes.xaxis.max = _eneg_sum_nr[_eneg_sum_nr.length-1][0];
              });

                   if (plot_eneg) {
                        plot_eneg.destroy();
                    }

                  plot2_eneg = $.jqplot('chart111', new_data ,options_eneg);
                  plot2_eneg.themeEngine.newTheme('uma', temp);
                  plot2_eneg.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_eneg").attr('disabled','disabled');
              $("#stop_auto_update_eneg").removeAttr('disabled');
        }


        function do_update_eneg() {
            var values = {
		        "device_info": device_info,
                "data_req": "energy_neg"
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);
				$.ajax({
				  url : '/pmtr_smap_update_eneg/',
				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',
				  success : function(data) {
					  console.log ("testing");
					  console.log (data);
                      update_plot_eneg(data);
				  },
				  error: function(data) {

                      clearTimeout(timeOut_eneg);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_eneg = setTimeout(do_update_eneg, 30000);
	}

    	  //Auto update the chart
	  $('#auto_update_eneg').click( function(evt){
          evt.preventDefault();
	      do_update_eneg();
	   });

      $('#stop_auto_update_eneg').click(function(){
          clearTimeout(timeOut_eneg);
          $('#stop_auto_update_eneg').attr('disabled', 'disabled');
          $('#auto_update_eneg').removeAttr('disabled');
      });

        $('#stack_chart_eneg').click( function(evt){
            evt.preventDefault();
	        stackCharts_eneg();
	   });

	  function stackCharts_eneg(){
        if (timeOut_eneg) {
          clearTimeout(timeOut_eneg);
          $('#stop_auto_update_eneg').attr('disabled', 'disabled');
          $('#auto_update_eneg').removeAttr('disabled');
        }
        options_eneg.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){
                   if (this.id == 'eneg_sum') {
                       new_data.push(_eneg_sum);
                   } else if (this.id == 'eneg_sum_nr') {
                       new_data.push(_eneg_sum_nr);
                   } else if (this.id == 'eneg_a') {
                       new_data.push(_eneg_a);
                   } else if (this.id == 'eneg_b') {
                       new_data.push(_eneg_b);
                   } else if (this.id == 'eneg_c') {
                       new_data.push(_eneg_c);
                   }
                   options_eneg.legend.labels.push(this.value);
                   options_eneg.axes.xaxis.min = _eneg_sum_nr[0][0];
                   options_eneg.axes.xaxis.max = _eneg_sum_nr[_eneg_sum_nr.length-1][0];
              });


                   if (plot_eneg) {
                        plot_eneg.destroy();
                    }

                  plot2_eneg = $.jqplot('chart111', new_data ,options_eneg);
                  plot2_eneg.themeEngine.newTheme('uma', temp);
                  plot2_eneg.activateTheme('uma');

      }


});