let ColorList = ["#3e95cd","#8e5ea2","#3cba9f","#e8c3b9", "#c45850"];
let value = {
	Product:{ key: ["XAUUSD", "XAGUSD", "BRTUSD", "LCOUSD"], value: ["Gold - United States Dollar", "Silver - United States Dollar", "Brent Crude Oil", "Light Crude Oil"] },
	Stock:{ key: ["TXN", "MSFT", "SBUX", "NKE"], value: ["Texas Instruments Incorporated", "Microsoft Corporation", "Starbucks Corporation", "Nike Inc" ] },
	Index:{ key: ["S&P", "NDX", "HSI", "DJI", "UKX"], value: ["S&P 500 Index", "NASDAQ-100", "Hang Seng Index", "Dow Jones Industrial Average", "FTSE 100 Index"] },
	Currency:{ key: ["USDCAD", "USDJPY", "GBPUSD", "EURUSD"], value: ["United States Dollar - Canadian Dollar", "United States Dollar - Japanese Yen", "Pound Sterling - United States Dollar", "Euro - United States Dollar"]}
};

jQuery(document).ready(function($){
	if( $('.floating-labels').length > 0 ) floatLabels();

	function floatLabels() {
		var inputFields = $('.floating-labels .cd-label').next();
		inputFields.each(function(){
			var singleInput = $(this);
			//check if user is filling one of the form fields 
			checkVal(singleInput);
			singleInput.on('change keyup', function(){
				checkVal(singleInput);	
			});
		});
	}

	function checkVal(inputField) {
		( inputField.val() == '' ) ? inputField.prev('.cd-label').removeClass('float') : inputField.prev('.cd-label').addClass('float');
	}

	getRandomNews();
});

var selectedDateRange = 1;
function changeDateBuffer(val){
	selectedDateRange = parseInt(val);
	self.getPrice(self.selectedDate, self.selectedProduct, self.selectedKey,self.selectedDateRange);
}

var selectedProduct = "Stock";
function changeProduct(val){
	selectedProduct = val;
	$('select[multiple]').empty();
	$('#productKey').find('option').remove().end();
	var productKeys = value[selectedProduct];
	for (var i = 0; i < productKeys.value.length; i++) {
		let value = productKeys.value[i];
		let key = productKeys.key[i];
		$('#productKey').append(`<option value="${key}">${value}</option>`);
	}
	selectedKey = productKeys.key[0];
	self.getPrice(self.selectedDate, self.selectedProduct, self.selectedKey,self.selectedDateRange);
}



var selectedKey = "TXN";
function changeKey(val){
	selectedKey = val;
	self.getPrice(self.selectedDate, self.selectedProduct, self.selectedKey, self.selectedDateRange);
}

function displayLineChart(data) {
	$('.chartjs-size-monitor').remove();
	$('#myChart').remove(); // this is my <canvas> element
  	$('#graph-container').append('<canvas id="myChart" width="400" height="200"><canvas>');
	new Chart($('#myChart'), {
	  type: 'line',
	  data: {
		labels: data.PriceDate,
		datasets: [{
			data: data.OpenPrice,
			label: "Open Price",
			borderColor: "#3e95cd",
			fill: false
		  }, {
			data: data.ClosePrice,
			label: "Close Price",
			borderColor: "#8e5ea2",
			fill: false
		  }, {
			data: data.Volume,
			label: "Volume",
			borderColor: "#3cba9f",
			fill: false
		  }
		]
	  },
	  options: {
		title: {
		  display: true,
		  text: data.Title
		}
	  }
	});
}

function getRandomNews() {
	//url: /source/random/:token/:date/:hash/:control
	let base_url = window.location.origin;
	let url = base_url + "/" + "random_news";
	hideLoading(false);
	$.get(url,
			function(status, jqXHR) { // success callback
				var data = jQuery.parseJSON(status);
				gameData = data;
				setupNews(gameData);
			}).done(function() { //Call Next Inform And Call Next Resource
				informUser('Request done!');
				hideLoading(true);
			}).fail(function(jqxhr, settings, ex) {
				hideLoading(true);
				informUser('failed, ' + ex);
	});
}

function getPrice(date, collection, key, range) {
    var data = JSON.stringify({ news_date:date, collection:collection , key: key, range:range});
    let base_url = window.location.origin;
    let url = base_url + "/" + "get_price";
    console.log(url);
    hideLoading(false);
    $.post(url, // url
        data, // data to be submit
        function(data, status, jqXHR) { // success callback
            console.log('status: ' + status + ', data: ' + data);
            var data = jQuery.parseJSON(data);
            self.displayLineChart(data)
        }).done(function() { //Call Next Inform And Call Next Resource
        	hideLoading(true);
            informUser('Request done!');
        }).fail(function(jqxhr, settings, ex) {
            hideLoading(true);
            informUser('failed, ' + ex);
    });
}

function hideLoading(hide) {
	if(hide){
		$('#loading').css('display','none');
		console.log("Hidden")
	}else{
		$('#loading').css('display','inline');
	}
}


function checkNewsCategory(category) {
    if (category.localeCompare("News") == 0){
        $('#cd-checkbox-1').prop('checked', true);
    }else if (category.localeCompare("Politics") == 0){
        $('#cd-checkbox-2').prop('checked', true);
    }else if (category.localeCompare("World") == 0){
        $('#cd-checkbox-3').prop('checked', true);
    }else if (category.localeCompare("Business") == 0){
        $('#cd-checkbox-4').prop('checked', true);
    }else if (category.localeCompare("Economy") == 0){
        $('#cd-checkbox-5').prop('checked', true);
    }else if (category.localeCompare("Economics") == 0){
        $('#cd-checkbox-6').prop('checked', true);
    }else if (category.localeCompare("News_") == 0){
        $('#cd-checkbox-7').prop('checked', true);
    }else if (category.localeCompare("Tech") == 0){
        $('#cd-checkbox-8').prop('checked', true);
    }else if (category.localeCompare("Kaggle") == 0){
        $('#cd-checkbox-9').prop('checked', true);
    }else if (category.localeCompare("Money") == 0){
        $('#cd-checkbox-10').prop('checked', true);
    }else if (category.localeCompare("Technology") == 0){
        $('#cd-checkbox-11').prop('checked', true);
    }else if (category.localeCompare("Energy") == 0){
        $('#cd-checkbox-12').prop('checked', true);
    }else if (category.localeCompare("Bonds") == 0){
        $('#cd-checkbox-13').prop('checked', true);
    }
}

function uncheckboxes() {
	var cbarray = $(':checkbox:checked');
	for (var i = 0; i < cbarray.length; i++) {
		$('#'+cbarray[i].id).prop('checked', false);
	}
}




var selectedDate = null;
function setupNews(news) {
    let news_title = $("#news_title");
	news_title.text(news.title);
    news_title.attr("href", news.url);
    $("#news_summery").html(news.summery);
    $("#news_category").html(news.category);
    $("#news_authors").html(news.authors.join(', '));
    $("#news_article").html(news.article);
    $("#news_date").html(news.news_date);
    self.selectedDate = news.news_date;
    self.getPrice(self.selectedDate, self.selectedProduct, self.selectedKey, self.selectedDateRange);
    checkNewsCategory(news.category);
}

/*
	Snackbar
*/
var informUser = function getUrlParameter(info) {
    var x = document.getElementById("snackbar");
    x.className = "show";
    x.innerHTML = info;
    setTimeout(function() {
        x.className = x.className.replace("show", "");
    }, 3000);
};