/**
 * Created by kruthika on 5/23/15.
 */
/**

 *  Authors: Kruthika Rathinavel
 *  Version: 2.0
 *  Email: kruthika@vt.edu
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"
**/

$(document).ready(function(){
    $.csrftoken();

    /**
     * Plot functions and values for Temperature
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */
    _indoor_temp = _temp;
	  //Plot options
	  var options_temp = {
			    legend: {
			      show: true,
			      labels:["Temperature"]
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

		            min : _indoor_temp[0][0],
		            max: _indoor_temp[_indoor_temp.length-1][0]
			      },
			      yaxis: {
			        autoscale: true,
			        label: "Temperature (F)"
			      }
			    }
	  };



	  //Initialize plot for power
      var data_points_temp = [_indoor_temp];
	  var plot_temp = $.jqplot('chart100', data_points_temp ,options_temp);
      $("#indoor_temp").attr('checked','checked');

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


        plot_temp.themeEngine.newTheme('uma', temp);
        plot_temp.activateTheme('uma');

        var timeOut_temp;

        function update_plot_temp(_data) {
            _indoor_temp = _data.temperature;


            var new_data = [];

              $.each($('input:checked'), function(index, value){

                   if (this.id == 'indoor_temp') {
                       new_data.push(_indoor_temp);
                       options_temp.legend.labels.push(this.value);
                   } else if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                       options_temp.legend.labels.push(this.value);
                   }

                   options_temp.axes.xaxis.min = _indoor_temp[0][0];
                   options_temp.axes.xaxis.max = _indoor_temp[_indoor_temp.length-1][0];
              });

                   if (plot_temp) {
                        plot_temp.destroy();
                    }


                  plot2_temp = $.jqplot('chart100', new_data ,options_temp);
                  plot2_temp.themeEngine.newTheme('uma', temp);
                  plot2_temp.activateTheme('uma');

              console.log('nowww');
              $("#auto_update_temp").attr('disabled','disabled');
              $("#stop_auto_update_temp").removeAttr('disabled');
        }


        function do_update_temp() {
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
				  url : '/weather_sensor_smap_update_temp/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {

					  console.log ("testing");
					  console.log (typeof(data));


                      update_plot_temp(data);

				  },
				  error: function(data) {

                      clearTimeout(timeOut_temp);
                      $('.bottom-right').notify({
					  	    message: { text: 'Communication Error. Try again later!'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
				  }
				 });
                timeOut_temp = setTimeout(do_update_temp, 30000);
			//},5000);
	}

    	  //Auto update the chart
	  $('#auto_update_temp').click( function(evt){
          evt.preventDefault();
	      do_update_temp();
	   });

      $('#stop_auto_update_temp').click(function(){
          clearTimeout(timeOut_temp);
          $('#stop_auto_update_temp').attr('disabled', 'disabled');
          $('#auto_update_temp').removeAttr('disabled');
      });

        $('#stack_chart_temp').click( function(evt){
            evt.preventDefault();
	        stackCharts_temp();
	   });

	  function stackCharts_temp(){
        if (timeOut_temp) {
          clearTimeout(timeOut_temp);
          $('#stop_auto_update_temp').attr('disabled', 'disabled');
          $('#auto_update_temp').removeAttr('disabled');
        }
        options_temp.legend.labels = [];
        var new_data = [];
        $.each($('input:checked'), function(index, value){

                   if (this.id == 'indoor_temp') {
                       new_data.push(_indoor_temp);
                       options_temp.legend.labels.push(this.value);
                   } else if (this.id == 'outdoor_temp') {
                       new_data.push(_outdoor_temp);
                       options_temp.legend.labels.push(this.value);
                   }


                   options_temp.axes.xaxis.min = _indoor_temp[0][0];
                   options_temp.axes.xaxis.max = _indoor_temp[_indoor_temp.length-1][0];
              });


                   if (plot_temp) {
                        plot_temp.destroy();
                    }


                  plot2_temp = $.jqplot('chart100', new_data ,options_temp);
                  plot2_temp.themeEngine.newTheme('uma', temp);
                  plot2_temp.activateTheme('uma');

      }

        /**
     * Plot functions and values for Humidity
     * @type {{legend: {show: boolean, labels: string[]}, series: *[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}, y2axis: {min: number, max: number, label: string}}}}
     */
        if (_humidity.length){
            //Plot options
            var options_humidity = {
                legend: {
                    show: true,
                    labels: ["Humidity"]
                },
                series: [{
                    label: 'Humidity (%)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                }],
                cursor: {
                    show: true,
                    zoom: true
                },
                seriesDefaults: {
                    show: true,
                    showMarker: false,
                    pointLabels: {show: false},
                    rendererOption: {smooth: true}
                },
                axesDefaults: {
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                axes: {
                    xaxis: {
                        label: "Time",
                        renderer: $.jqplot.DateAxisRenderer,
                        tickOptions: {formatString: '%m/%d, %H:%M'},

                        min: _humidity[0][0],
                        max: _humidity[_humidity.length - 1][0]
                    },
                    yaxis: {
                        autoscale: true,
                        label: "Humidity (%)"
                    }
                }
            };


            //Initialize plot for power
            var data_points_humidity = [_humidity];
            var plot_humidity = $.jqplot('chart101', data_points_humidity, options_humidity);
            $("#indoor_humidity").attr('checked', 'checked');

            temp = {
                seriesStyles: {
                    seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                    highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
                },
                grid: {},
                axesStyles: {
                    borderWidth: 0,
                    label: {
                        fontFamily: 'Sans',
                        textColor: 'white',
                        fontSize: '9pt'
                    }
                }
            };


            plot_humidity.themeEngine.newTheme('uma', temp);
            plot_humidity.activateTheme('uma');

            var timeOut_humidity;

            function update_plot_humidity(_data) {
                _indoor_humidity = _data.humidity;


                var new_data = [];

                $.each($('input:checked'), function (index, value) {

                    if (this.id == 'indoor_humidity') {
                        new_data.push(_indoor_humidity);
                        options_humidity.legend.labels.push(this.value);
                    } else if (this.id == 'outdoor_humidity') {
                        new_data.push(_outdoor_humidity);
                        options_humidity.legend.labels.push(this.value);
                    }

                    options_humidity.axes.xaxis.min = _indoor_humidity[0][0];
                    options_humidity.axes.xaxis.max = _indoor_humidity[_indoor_humidity.length - 1][0];
                });

                if (plot_humidity) {
                    plot_humidity.destroy();
                }


                plot2_humidity = $.jqplot('chart101', new_data, options_humidity);
                plot2_humidity.themeEngine.newTheme('uma', temp);
                plot2_humidity.activateTheme('uma');

                console.log('nowww');
                $("#auto_update_humidity").attr('disabled', 'disabled');
                $("#stop_auto_update_humidity").removeAttr('disabled');
            }


            function do_update_humidity() {
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
                    url: '/weather_sensor_smap_update_humidity/',

                    type: 'POST',
                    data: jsonText,
                    dataType: 'json',

                    success: function (data) {

                        console.log("testing");
                        console.log(data);
                        update_plot_humidity(data);

                    },
                    error: function (data) {

                        clearTimeout(timeOut_humidity);
                        $('.bottom-right').notify({
                            message: {text: 'Communication Error. Try again later!'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
                    }
                });
                timeOut_humidity = setTimeout(do_update_humidity, 30000);
            }

            //Auto update the chart
            $('#auto_update_humidity').click(function (evt) {
                evt.preventDefault();
                do_update_humidity();
            });

            $('#stop_auto_update_humidity').click(function () {
                clearTimeout(timeOut_humidity);
                $('#stop_auto_update_humidity').attr('disabled', 'disabled');
                $('#auto_update_humidity').removeAttr('disabled');
            });

            $('#stack_chart_humidity').click(function (evt) {
                evt.preventDefault();
                stackCharts_humidity();
            });

            function stackCharts_humidity() {
                if (timeOut_humidity) {
                    clearTimeout(timeOut_humidity);
                    $('#stop_auto_update_humidity').attr('disabled', 'disabled');
                    $('#auto_update_humidity').removeAttr('disabled');
                }
                options_humidity.legend.labels = [];
                var new_data = [];
                $.each($('input:checked'), function (index, value) {

                    if (this.id == 'indoor_humidity') {
                        new_data.push(_indoor_humidity);
                        options_humidity.legend.labels.push(this.value);
                    } else if (this.id == 'outdoor_humidity') {
                        new_data.push(_outdoor_humidity);
                        options_humidity.legend.labels.push(this.value);
                    }


                    options_humidity.axes.xaxis.min = _indoor_humidity[0][0];
                    options_humidity.axes.xaxis.max = _indoor_humidity[_indoor_humidity.length - 1][0];
                });


                if (plot_humidity) {
                    plot_humidity.destroy();
                }


                plot2_humidity = $.jqplot('chart101', new_data, options_humidity);
                plot2_humidity.themeEngine.newTheme('uma', temp);
                plot2_humidity.activateTheme('uma');

            }


        }
    /**
     * Plot functions and values for CO2
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
        if (_co2.length) {
            var options_co2 = {
                legend: {
                    show: true,
                    labels: ["CO2"]
                },
                series: [{
                    label: 'CO2 (ppm)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                }],
                cursor: {
                    show: true,
                    zoom: true
                },
                seriesDefaults: {
                    show: true,
                    showMarker: false,
                    pointLabels: {show: false},
                    rendererOption: {smooth: true}
                },
                axesDefaults: {
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                axes: {
                    xaxis: {
                        label: "Time",
                        renderer: $.jqplot.DateAxisRenderer,
                        tickOptions: {formatString: '%m/%d, %H:%M'},

                        min: _co2[0][0],
                        max: _co2[_co2.length - 1][0]
                    },
                    yaxis: {
                        autoscale: true,
                        label: "CO2 (ppm)"
                    }
                }
            };


            //Initialize plot for voltage
            var data_points_co2 = [_co2];
            var plot_co2 = $.jqplot('chart103', data_points_co2, options_co2);
            $("#co2").attr('checked', 'checked');

            temp = {
                seriesStyles: {
                    seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                    highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
                },
                grid: {},
                axesStyles: {
                    borderWidth: 0,
                    label: {
                        fontFamily: 'Sans',
                        textColor: 'white',
                        fontSize: '9pt'
                    }
                }
            };


            plot_co2.themeEngine.newTheme('uma', temp);
            plot_co2.activateTheme('uma');

            var timeOut_co2;

            function update_plot_co2(_data) {
                _co2 = _data.co2;

                var new_data = [];

                $.each($('input:checked'), function (index, value) {

                    if (this.id == 'co2') {
                        if (typeof(_co2) == 'string') {
                            _co2 = $.parseJSON(_co2);
                        }
                        new_data.push(_co2);
                        options_co2.legend.labels.push(this.value);
                    }

                    options_co2.axes.xaxis.min = _co2[0][0];
                    options_co2.axes.xaxis.max = _co2[_co2.length - 1][0];
                });

                if (plot_co2) {
                    plot_co2.destroy();
                }


                plot2_co2 = $.jqplot('chart103', new_data, options_co2);
                plot2_co2.themeEngine.newTheme('uma', temp);
                plot2_co2.activateTheme('uma');

                console.log('nowww');
                $("#auto_update_co2").attr('disabled', 'disabled');
                $("#stop_auto_update_co2").removeAttr('disabled');
            }


            function do_update_co2() {
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
                    url: '/weather_sensor_smap_update_co2/',

                    type: 'POST',
                    data: jsonText,
                    dataType: 'json',

                    success: function (data) {

                        console.log("testing");
                        console.log(data);
                        update_plot_co2(data);

                    },
                    error: function (data) {

                        clearTimeout(timeOut_co2);
                        $('.bottom-right').notify({
                            message: {text: 'Communication Error. Try again later!'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
                    }
                });
                timeOut_co2 = setTimeout(do_update_co2, 30000);
            }

            //Auto update the chart
            $('#auto_update_co2').click(function (evt) {
                evt.preventDefault();
                do_update_co2();
            });

            $('#stop_auto_update_co2').click(function () {
                clearTimeout(timeOut_co2);
                $('#stop_auto_update_co2').attr('disabled', 'disabled');
                $('#auto_update_co2').removeAttr('disabled');
            });

            $('#stack_chart_co2').click(function (evt) {
                evt.preventDefault();
                stackCharts_co2();
            });

            function stackCharts_co2() {
                if (timeOut_co2) {
                    clearTimeout(timeOut_co2);
                    $('#stop_auto_update_co2').attr('disabled', 'disabled');
                    $('#auto_update_co2').removeAttr('disabled');
                }
                options_co2.legend.labels = [];
                var new_data = [];
                $.each($('input:checked'), function (index, value) {
                    if (this.id == 'co2') {
                        if (typeof(_co2) == 'string') {
                            _co2 = $.parseJSON(_co2);
                        }
                        new_data.push(_co2);
                        options_co2.legend.labels.push(this.value);
                    }

                    options_co2.axes.xaxis.min = _co2[0][0];
                    options_co2.axes.xaxis.max = _co2[_co2.length - 1][0];
                });


                if (plot_co2) {
                    plot_co2.destroy();
                }


                plot2_co2 = $.jqplot('chart103', new_data, options_co2);
                plot2_co2.themeEngine.newTheme('uma', temp);
                plot2_co2.activateTheme('uma');

            }

        }
    /**
     * Plot functions and values for Pressure
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
        if (_pressure.length) {
            var options_pressure = {
                legend: {
                    show: true,
                    labels: ["Pressure"]
                },
                series: [{
                    label: 'Pressure (Pa)',
                    neighborThreshold: -1,
                    yaxis: 'yaxis'
                }],
                cursor: {
                    show: true,
                    zoom: true
                },
                seriesDefaults: {
                    show: true,
                    showMarker: false,
                    pointLabels: {show: false},
                    rendererOption: {smooth: true}
                },
                axesDefaults: {
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                axes: {
                    xaxis: {
                        label: "Time",
                        renderer: $.jqplot.DateAxisRenderer,
                        tickOptions: {formatString: '%m/%d, %H:%M'},

                        min: _pressure[0][0],
                        max: _pressure[_pressure.length - 1][0]
                    },
                    yaxis: {
                        autoscale: true,
                        label: "Pressure (Pa)"
                    }
                }
            };


            //Initialize plot for voltage
            var data_points_pressure = [_pressure];
            var plot_pressure = $.jqplot('chart102', data_points_pressure, options_pressure);
            $("#pressure").attr('checked', 'checked');

            temp = {
                seriesStyles: {
                    seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                    highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
                },
                grid: {},
                axesStyles: {
                    borderWidth: 0,
                    label: {
                        fontFamily: 'Sans',
                        textColor: 'white',
                        fontSize: '9pt'
                    }
                }
            };


            plot_pressure.themeEngine.newTheme('uma', temp);
            plot_pressure.activateTheme('uma');

            var timeOut_pressure;

            function update_plot_pressure(_data) {
                _pressure = _data.pressure;

                var new_data = [];

                $.each($('input:checked'), function (index, value) {

                    if (this.id == 'pressure') {

                        if (typeof(_pressure) == 'string') {
                            _pressure = $.parseJSON(_pressure);
                        }
                        new_data.push(_pressure);
                        options_pressure.legend.labels.push(this.value);
                    }

                    options_pressure.axes.xaxis.min = _pressure[0][0];
                    options_pressure.axes.xaxis.max = _pressure[_pressure.length - 1][0];
                });

                if (plot_pressure) {
                    plot_pressure.destroy();
                }


                plot2_pressure = $.jqplot('chart102', new_data, options_pressure);
                plot2_pressure.themeEngine.newTheme('uma', temp);
                plot2_pressure.activateTheme('uma');

                console.log('nowww');
                $("#auto_update_pressure").attr('disabled', 'disabled');
                $("#stop_auto_update_pressure").removeAttr('disabled');
            }


            function do_update_pressure() {
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
                    url: '/weather_sensor_smap_update_pressure/',

                    type: 'POST',
                    data: jsonText,
                    dataType: 'json',

                    success: function (data) {

                        console.log("testing");
                        console.log(data);
                        update_plot_pressure(data);

                    },
                    error: function (data) {

                        clearTimeout(timeOut_pressure);
                        $('.bottom-right').notify({
                            message: {text: 'Communication Error. Try again later!'},
                            type: 'blackgloss',
                            fadeOut: {enabled: true, delay: 5000}
                        }).show();
                    }
                });
                timeOut_pressure = setTimeout(do_update_pressure, 30000);
                //},5000);
            }

            //Auto update the chart
            $('#auto_update_pressure').click(function (evt) {
                evt.preventDefault();
                do_update_pressure();
            });

            $('#stop_auto_update_pressure').click(function () {
                clearTimeout(timeOut_pressure);
                $('#stop_auto_update_pressure').attr('disabled', 'disabled');
                $('#auto_update_pressure').removeAttr('disabled');
            });

            $('#stack_chart_pressure').click(function (evt) {
                evt.preventDefault();
                stackCharts_pressure();
            });

            function stackCharts_pressure() {
                if (timeOut_pressure) {
                    clearTimeout(timeOut_pressure);
                    $('#stop_auto_update_pressure').attr('disabled', 'disabled');
                    $('#auto_update_pressure').removeAttr('disabled');
                }
                options_pressure.legend.labels = [];
                var new_data = [];
                $.each($('input:checked'), function (index, value) {
                    if (this.id == 'pressure') {
                        if (typeof(_pressure) == 'string') {
                            _pressure = $.parseJSON(_pressure);
                        }
                        new_data.push(_pressure);
                        options_pressure.legend.labels.push(this.value);
                    }

                    options_pressure.axes.xaxis.min = _pressure[0][0];
                    options_pressure.axes.xaxis.max = _pressure[_pressure.length - 1][0];
                });


                if (plot_pressure) {
                    plot_pressure.destroy();
                }


                plot2_pressure = $.jqplot('chart103', new_data, options_pressure);
                plot2_pressure.themeEngine.newTheme('uma', temp);
                plot2_pressure.activateTheme('uma');

            }
        }
        /**
     * Plot functions and values for Noise
     * @type {{legend: {show: boolean, labels: string[]}, series: {label: string, neighborThreshold: number, yaxis: string}[], cursor: {show: boolean, zoom: boolean}, seriesDefaults: {show: boolean, showMarker: boolean, pointLabels: {show: boolean}, rendererOption: {smooth: boolean}}, axesDefaults: {labelRenderer: jQuery.jqplot.CanvasAxisLabelRenderer}, axes: {xaxis: {label: string, renderer: jQuery.jqplot.DateAxisRenderer, tickOptions: {formatString: string}, numberTicks: number, min: *, max: *}, yaxis: {min: number, max: number, label: string}}}}
     */
	  //Plot options
            if (_noise.length) {
                var options_noise = {
                    legend: {
                        show: true,
                        labels: ["Noise"]
                    },
                    series: [{
                        label: 'Noise (db)',
                        neighborThreshold: -1,
                        yaxis: 'yaxis'
                    }],
                    cursor: {
                        show: true,
                        zoom: true
                    },
                    seriesDefaults: {
                        show: true,
                        showMarker: false,
                        pointLabels: {show: false},
                        rendererOption: {smooth: true}
                    },
                    axesDefaults: {
                        labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                    },
                    axes: {
                        xaxis: {
                            label: "Time",
                            renderer: $.jqplot.DateAxisRenderer,
                            tickOptions: {formatString: '%m/%d, %H:%M'},

                            min: _noise[0][0],
                            max: _noise[_noise.length - 1][0]
                        },
                        yaxis: {
                            autoscale: true,
                            label: "Noise (db)"
                        }
                    }
                };


                //Initialize plot for voltage
                var data_points_noise = [_noise];
                var plot_noise = $.jqplot('chart104', data_points_noise, options_noise);
                $("#noise").attr('checked', 'checked');

                temp = {
                    seriesStyles: {
                        seriesColors: ['red', 'orange', 'yellow', 'green', 'blue', 'indigo'],
                        highlightColors: ['lightpink', 'lightsalmon', 'lightyellow', 'lightgreen', 'lightblue', 'mediumslateblue']
                    },
                    grid: {},
                    axesStyles: {
                        borderWidth: 0,
                        label: {
                            fontFamily: 'Sans',
                            textColor: 'white',
                            fontSize: '9pt'
                        }
                    }
                };


                plot_noise.themeEngine.newTheme('uma', temp);
                plot_noise.activateTheme('uma');

                var timeOut_noise;

                function update_plot_noise(_data) {
                    _noise = _data.noise;

                    var new_data = [];

                    $.each($('input:checked'), function (index, value) {

                        if (this.id == 'noise') {
                            if (typeof(_noise) == 'string') {
                                _noise = $.parseJSON(_noise);
                            }
                            new_data.push(_noise);
                            options_noise.legend.labels.push(this.value);
                        }

                        options_noise.axes.xaxis.min = _noise[0][0];
                        options_noise.axes.xaxis.max = _noise[_noise.length - 1][0];
                    });

                    if (plot_noise) {
                        plot_noise.destroy();
                    }


                    plot2_noise = $.jqplot('chart104', new_data, options_noise);
                    plot2_noise.themeEngine.newTheme('uma', temp);
                    plot2_noise.activateTheme('uma');

                    console.log('nowww');
                    $("#auto_update_noise").attr('disabled', 'disabled');
                    $("#stop_auto_update_noise").removeAttr('disabled');
                }


                function do_update_noise() {
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
                        url: '/weather_sensor_smap_update_noise/',

                        type: 'POST',
                        data: jsonText,
                        dataType: 'json',

                        success: function (data) {

                            console.log("testing");
                            console.log(data);
                            update_plot_noise(data);

                        },
                        error: function (data) {

                            clearTimeout(timeOut_noise);
                            $('.bottom-right').notify({
                                message: {text: 'Communication Error. Try again later!'},
                                type: 'blackgloss',
                                fadeOut: {enabled: true, delay: 5000}
                            }).show();
                        }
                    });
                    timeOut_noise = setTimeout(do_update_noise, 30000);
                    //},5000);
                }

                //Auto update the chart
                $('#auto_update_noise').click(function (evt) {
                    evt.preventDefault();
                    do_update_noise();
                });

                $('#stop_auto_update_noise').click(function () {
                    clearTimeout(timeOut_noise);
                    $('#stop_auto_update_noise').attr('disabled', 'disabled');
                    $('#auto_update_noise').removeAttr('disabled');
                });

                $('#stack_chart_noise').click(function (evt) {
                    evt.preventDefault();
                    stackCharts_noise();
                });

                function stackCharts_noise() {
                    if (timeOut_noise) {
                        clearTimeout(timeOut_noise);
                        $('#stop_auto_update_noise').attr('disabled', 'disabled');
                        $('#auto_update_noise').removeAttr('disabled');
                    }
                    options_noise.legend.labels = [];
                    var new_data = [];
                    $.each($('input:checked'), function (index, value) {
                        if (this.id == 'noise') {
                            if (typeof(_noise) == 'string') {
                                _noise = $.parseJSON(_noise);
                            }
                            new_data.push(_noise);
                            options_noise.legend.labels.push(this.value);
                        }

                        options_noise.axes.xaxis.min = _noise[0][0];
                        options_noise.axes.xaxis.max = _noise[_noise.length - 1][0];
                    });


                    if (plot_noise) {
                        plot_noise.destroy();
                    }


                    plot2_noise = $.jqplot('chart104', new_data, options_noise);
                    plot2_noise.themeEngine.newTheme('uma', temp);
                    plot2_noise.activateTheme('uma');

                }
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
				  url : '/charts/' + mac + '/',

				  type: 'POST',
                  data: jsonText,
                  dataType: 'json',

				  success : function(data) {



                      if (data.temperature.length == 0) {
                          $('.bottom-right').notify({
					  	    message: { text: 'No data found for the selected time period.'},
					  	    type: 'blackgloss',
                          fadeOut: { enabled: true, delay: 5000 }
					  	  }).show();
                      } else {

                          update_plot_temp(data);
                          $("#auto_update_temp").removeAttr('disabled');
                          $("#stop_auto_update_temp").attr('disabled','disabled');
                          update_plot_humidity(data);
                          $("#auto_update_humidity").removeAttr('disabled');
                          $("#stop_auto_update_humidity").attr('disabled','disabled');
                          update_plot_pressure(data);
                          $("#auto_update_pressure").removeAttr('disabled');
                          $("#stop_auto_update_pressure").attr('disabled','disabled');
                          update_plot_noise(data);
                          $("#auto_update_co2").removeAttr('disabled');
                          $("#stop_auto_update_co2").attr('disabled','disabled');
                          update_plot_co2(data);
                          $("#auto_update_noise").removeAttr('disabled');
                          $("#stop_auto_update_noise").attr('disabled','disabled');

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