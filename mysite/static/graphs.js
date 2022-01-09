fetch('/api/data.json')
	.then(function (response) {
		return response.json();
	})
	.then(function (json) {
		let serieses = createGraph(json.series);
		renderCharts(serieses);
		document.getElementById('alert_holder').innerHTML = '';
	})
	.catch(function (error) {
		//Something went wrong
		console.log(error);
	});

function createGraph(data) {
	let serieses = {};
	
	for (const [group, lists] of Object.entries(data)) {
		serieses[group] = []
		serieses[group].push({ name: 'vaxed', points: lists['vaxed'] });
		serieses[group].push({ name: 'unvaxed', points: lists['unvaxed'] });
	}
	
	return serieses;
}

function renderChart(series, group, msg) {
	JSC.Chart(group, {
		title_label_text: msg,
		defaultPoint_tooltip: '%icon %seriesName: <b>%yValue</b> cases per 100k',
		series: series,
		xAxis: { 
			scale_type: 'time', 
			crosshair: { 
			  enabled: true, 
			  label_text: '{%value:date y}'
			}
		},
		defaultPoint: { 
			marker_visible: false
		  },
		legend: {
			template: '%icon %name'
		},
		annotations: [{
			label_text: 'Data provided by Act Now Covid, Marin HHS, and California HHS',
			position: 'bottom left'
		}],
	});
}

function renderCharts(serieses) {
	all_series = [];
	for (const [group, series] of Object.entries(serieses)) {
		if (document.getElementById(group)) {
			renderChart(series, group, 'Average daily covid cases/100k among people ages <b>' + group + '</b> for the previous week');
		}
		if (group == '0-4') {
			all_series.push({name: group, points: series[1].points})
		} else {
			all_series.push({name: group, points: series[0].points})
		}
	}
	console.log(all_series)
	renderChart(all_series, 'all graph', 'Average daily covid cases/100k for vaccinated people and 0-4 year olds')
}