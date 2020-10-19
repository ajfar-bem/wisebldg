/**

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
			      labels:["Power AC"]
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

		            min : Power_ac[0][0],
		            max: Power_ac[Power_ac.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Power (W)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_power = [Power_ac];
	  var plot_power = $.jqplot('chart_power', data_points_power ,options_power);
      $("#Power_ac").attr('checked','checked');

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
            Power_ac = _data.power_ac;


            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'Power_ac') {
                       new_data.push(Power_ac);
                        options_power.legend.labels.push(this.value);
                   }

                   options_power.axes.xaxis.min = Power_ac[0][0];
                   options_power.axes.xaxis.max = Power_ac[Power_ac.length-1][0];
              });

                   if (plot_power) {
                        plot_power.destroy();
                    }


                  plot2_power = $.jqplot('chart_power', new_data ,options_power);
                  plot2_power.themeEngine.newTheme('uma', temp);
                  plot2_power.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_power").attr('disabled','disabled');
              $("#stop_auto_update_power").removeAttr('disabled');
        }


        function do_update_power() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
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

                   if (this.id == 'Power_ac') {
                       new_data.push(Power_ac);
                       options_power.legend.labels.push(this.value);
                   }

                   options_power.axes.xaxis.min = _power_sum[0][0];
                   options_power.axes.xaxis.max = _power_sum[_power_sum.length-1][0];
              });


                   if (plot_power) {
                        plot_power.destroy();
                    }


                  plot2_power = $.jqplot('chart_power', new_data ,options_power);
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
			      labels:["Voltage PV", "Voltage AC"]
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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

		            min : Vac[0][0],
		            max: Vac[Vac.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Voltage (Volts)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_voltage = [Vpv,Vac];
	  var plot_voltage = $.jqplot('chart_voltage', data_points_voltage ,options_voltage);
      $("#Vpv").attr('checked','checked');
      $("#Vac").attr('checked','checked');

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


        plot_voltage.themeEngine.newTheme('uma', temp);
        plot_voltage.activateTheme('uma');

        var timeOut_voltage;

        function update_plot_voltage(_data) {
            Vpv= _data.Vpv;

            Vac = _data.Vac;

            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'Vpv') {
                       new_data.push(Vpv);
                       options_voltage.legend.labels.push(this.value);
                   } else if (this.id == 'Vac') {
                       new_data.push(Vac);
                       options_voltage.legend.labels.push(this.value);
                   }
                   options_voltage.axes.xaxis.min = Vpv[0][0];
                   options_voltage.axes.xaxis.max = Vpv[Vpv.length-1][0];
              });

                   if (plot_voltage) {
                        plot_voltage.destroy();
                    }


                  plot2_voltage = $.jqplot('chart_voltage', new_data ,options_voltage);
                  plot2_voltage.themeEngine.newTheme('uma', temp);
                  plot2_voltage.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_voltage").attr('disabled','disabled');
              $("#stop_auto_update_voltage").removeAttr('disabled');
        }


        function do_update_voltage() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/solar_smap_update_voltage/',

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

                   if (this.id == 'Vac') {
                       new_data.push(Vac);
                       options_voltage.legend.labels.push(this.value);
                   } else if (this.id == 'Vpv') {
                       new_data.push(Vpv);
                       options_voltage.legend.labels.push(this.value);
                   }
                   options_voltage.axes.xaxis.min = Vac[0][0];
                   options_voltage.axes.xaxis.max = Vac[Vac.length-1][0];
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
			      labels:["Ipv", "Iac"]
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
			        tickOptions:{formatString:'%m/%d, %H:%M'},

		            min : Ipv[0][0],
		            max: Ipv[Ipv.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Current (A)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_current = [Ipv,Iac];
	  var plot_current = $.jqplot('chart_current', data_points_current ,options_current);
      $("#Ipv").attr('checked','checked');
      $("#Iac").attr('checked','checked');

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


        plot_current.themeEngine.newTheme('uma', temp);
        plot_current.activateTheme('uma');

        var timeOut_current;

        function update_plot_current(_data) {
            Ipv = _data.Ipv;

            Iac = _data.Iac;


            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'Ipv') {
                       new_data.push(Ipv);
                       options_current.legend.labels.push(this.value);
                   } else if (this.id == 'Iac') {
                       new_data.push(Iac);
                       options_current.legend.labels.push(this.value);
                   }

                   options_current.axes.xaxis.min = Ipv[0][0];
                   options_current.axes.xaxis.max = Ipv[Ipv.length-1][0];
              });

                   if (plot_current) {
                        plot_current.destroy();
                    }


                  plot2_current = $.jqplot('chart_current', new_data ,options_current);
                  plot2_current.themeEngine.newTheme('uma', temp);
                  plot2_current.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_current").attr('disabled','disabled');
              $("#stop_auto_update_current").removeAttr('disabled');
        }


        function do_update_current() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/solar_smap_update_current/',

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

                   if (this.id == 'Ipv') {
                       new_data.push(Ipv);
                       options_current.legend.labels.push(this.value);
                   } else if (this.id == 'Iac') {
                       new_data.push(_current_b);
                       options_current.legend.labels.push(this.value);
                   }
                   options_current.axes.xaxis.min = _current_a[0][0];
                   options_current.axes.xaxis.max = _current_a[_current_a.length-1][0];
              });


                   if (plot_current) {
                        plot_current.destroy();
                    }


                  plot2_current = $.jqplot('chart_current', new_data ,options_current);
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
			      labels:["Ambient Temperature", "Module Temperature"]
			    },
                series:[{
                    label: 'Temperature (F)',
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

		            min : Temperature_ambient[0][0],
		            max: Temperature_ambient[Temperature_ambient.length-1][0]
			      },
			      yaxis: {
                    autoscale: true,
			        label: "Temperature (F)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pf = [Temperature_ambient, Temperature_module];
	  var plot_pf = $.jqplot('chart_temperature', data_points_pf ,options_pf);
      $("#Temperature_ambient").attr('checked','checked');
      $("#Temperature_module").attr('checked','checked');


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


        plot_pf.themeEngine.newTheme('uma', temp);
        plot_pf.activateTheme('uma');

        var timeOut_pf;

        function update_plot_temperature(_data) {
            Temperature_module = _data.Temperature_module;

            Temperature_module = _data.Temperature_module;


            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'Temperature_module') {
                       new_data.push(Temperature_module);
                       options_pf.legend.labels.push(this.value);
                   } else if (this.id == 'Temperature_ambient') {
                       new_data.push(Temperature_ambient);
                       options_pf.legend.labels.push(this.value);
                   }

                   options_pf.axes.xaxis.min = Temperature_module[0][0];
                   options_pf.axes.xaxis.max = Temperature_module[Temperature_module.length-1][0];
              });

                   if (plot_pf) {
                        plot_pf.destroy();
                    }


                  plot2_pf = $.jqplot('chart_temperature', new_data ,options_pf);
                  plot2_pf.themeEngine.newTheme('uma', temp);
                  plot2_pf.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pf").attr('disabled','disabled');
              $("#stop_auto_update_pf").removeAttr('disabled');
        }


        function do_update_temperature() {
            var from_date = $("#from_date").val();
            var to_date = $("#to_date").val();
            var values = {
		        "mac": mac,
                "from_dt": from_date,
                "to_dt": to_date
		    };
	        var jsonText = JSON.stringify(values);
            console.log(jsonText);

				$.ajax({
				  url : '/solar_smap_update_energy/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {

					  console.log ("testing");
					  console.log (data);
                      update_plot_temperature(data);

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
                timeOut_pf = setTimeout(do_update_temperature, 30000);

	}
    function update_plot_wind(_data) {
            Wind_velocity = _data.Wind_velocity;



            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'Wind_velocity') {
                       new_data.push(Wind_velocity);
                       options_wind.legend.labels.push(this.value);
                   }
                   options_wind.axes.xaxis.min = Wind_velocity[0][0];
                   options_wind.axes.xaxis.max = Wind_velocity[Wind_velocity.length-1][0];
              });

                   if (plot_wind) {
                        plot_wind.destroy();
                    }


                  plot2_pf = $.jqplot('chart_wind', new_data ,options_wind);
                  plot2_pf.themeEngine.newTheme('uma', temp);
                  plot2_pf.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_pf").attr('disabled','disabled');
              $("#stop_auto_update_pf").removeAttr('disabled');
        }
    	  //Auto update the chart
	  $('#auto_update_pf').click( function(evt){
          evt.preventDefault();
	      do_update_temperature();
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

                   if (this.id == 'Energy_total') {
                       new_data.push(Energy_total);
                       options_pf.legend.labels.push(this.value);
                   } else if (this.id == 'Energy_day') {
                       new_data.push(Energy_day);
                       options_pf.legend.labels.push(this.value);
                   }

                   options_pf.axes.xaxis.min = _pf_avg[0][0];
                   options_pf.axes.xaxis.max = _pf_avg[_pf_avg.length-1][0];
              });


                   if (plot_pf) {
                        plot_pf.destroy();
                    }


                  plot2_pf = $.jqplot('chart_energy', new_data ,options_pf);
                  plot2_pf.themeEngine.newTheme('uma', temp);
                  plot2_pf.activateTheme('uma');

      }

     $("#get_stat").click(function(evt) {
        evt.preventDefault();
        var from_date = $("#from_date").val();
        var to_date = $("#to_date").val();
        get_statistics(from_date, to_date);

    });


    var options_wind = {
			    legend: {
			      show: true,
			      labels:["Wind Velocity"]
			    },
                series:[{
                    label: 'Velocity (m/s)',
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

		            min : Wind_velocity[0][0],
		            max: Wind_velocity[Wind_velocity.length-1][0]
			      },
			      yaxis: {
                    autoscale: true,
			        label: "Velocity (m/s)"
			      }
			    }
	  };



	  //Initialize plot for voltage
      var data_points_pf = [Wind_velocity];
	  var plot_wind = $.jqplot('chart_wind', data_points_pf ,options_wind);
      $("#Wind_velocity").attr('checked','checked');


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


        plot_wind.themeEngine.newTheme('uma', temp);
        plot_wind.activateTheme('uma');




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



                      if (data.power_ac.length == 0) {
                          $('.bottom-right').notify({
					  	    message: { text: 'No data found for the selected time period.'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
                      } else {
                          update_plot_power(data);
                          $("#auto_update_power").removeAttr('disabled');
                          $("#stop_auto_update_power").attr('disabled', 'disabled');
                          update_plot_voltage(data);
                          $("#auto_update_voltage").removeAttr('disabled');
                          $("#stop_auto_update_voltage").attr('disabled', 'disabled');
                          update_plot_current(data);
                          $("#auto_update_current").removeAttr('disabled');
                          $("#stop_auto_update_current").attr('disabled', 'disabled');
                          update_plot_temperature(data);

                          $("#auto_update_pf").removeAttr('disabled');
                          $("#stop_auto_update_pf").attr('disabled', 'disabled');
                          update_plot_wind(data);
                      }

				  },
				  error: function(jqXHR, textStatus, errorThrown) {
                      console.log(errorThrown)

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
              url : 'charts/download_sheet/' + mac + '/',
              type: 'POST',
              data: jsonText,
              dataType: 'json',
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