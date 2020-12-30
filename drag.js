const list_items = document.querySelectorAll('.list-item');
const lists = document.querySelectorAll('.list');

var prereq_arr = new Array(9);    
for (var i = 0; i < prereq_arr.length; i++) { 
    prereq_arr[i] = new Array(10); 
} 
var credits_arr = [0,0,0,0,0,0,0,0,0,0]; 
var index = [0,0,0,0,0,0,0,0,0,0];


prereq_arr[0] = courses_taken_list; 
for(var t=0; t < courses_list.length; t++){
	prereq_arr[t+1] = courses_list[t];
	
	for(var c in courses_list[t]){
		(index[t+1])++;
		var key3 = courses_list[t][c];
		var curr_credits = credits_list[key3];
		if(curr_credits === undefined){
			curr_credits = 3;
		}	

		credits_arr[t+1] = credits_arr[t+1] + curr_credits;
	}
	
}


let draggedItem = null;
var flag = 0;
var flag1 = 0;


for (let i = 0; i < list_items.length; i++) {
	const item = list_items[i];

	item.addEventListener('dragstart', function () {
		draggedItem = item;
		setTimeout(function () {
			item.style.display = 'none';
		}, 0)
	});

	item.addEventListener('dragend', function () {
		setTimeout(function () {
			draggedItem.style.cssText = 'background-color: #F3F3F3; border-radius: 8px; padding: 15px 20px; text-align: center; margin: 4px 0px; display: inline-block;';
			draggedItem = null;
		}, 0);
	})

	for (let j = 0; j < lists.length; j ++) {
		const list = lists[j];

		list.addEventListener('dragover', function (e) {
			e.preventDefault();
		});
		
		list.addEventListener('dragenter', function (e) {
			e.preventDefault();
			this.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
		});

		list.addEventListener('dragleave', function (e) {
			this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
		});

		list.addEventListener('drop', function (e) {
			// console.log('drop');
			//Check for prerequsites
			if (draggedItem !== null) {
				var prereqnum = 0;
				var countnum = 0;
				var semester = 0;
				semester = null;
				
				console.log(credits_arr);
				console.log(prereq_arr);
				if(this.getAttribute('name') == "courses-list" || this.getAttribute('name') == "credit-courses"){
					this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
					this.append(draggedItem);
					if (this.getAttribute('name') == "credit-courses" && flag1 == 0) {
						flag1 = 0;
						if (!(prereq_arr[0].includes(draggedItem.innerHTML)))
						{
							prereq_arr[0].push(draggedItem.innerHTML);
						}
						var creditName = "courses-w-credit";
						draggedItem.setAttribute("name",creditName);
						return;
					}
					else {
						draggedItem.removeAttribute('name');
					}
					for (var s = 1; s < 9; s++)
					{
						if (prereq_arr[s].includes(draggedItem.innerHTML) && flag1 == 0)
						{
							flag1 = 1;
							var itemIndex = prereq_arr[s].indexOf(draggedItem.innerHTML);
							prereq_arr[s].splice(itemIndex, 1);
							var idx = index[s];
							index[s] = idx-1;
							var key2 = draggedItem.textContent;

							//Check credits
							var curr_credits = credits_list[key2];
							if(curr_credits === undefined){
								curr_credits = 3;
							}
						
							if (credits_arr[s] - curr_credits < 0)
							{
								credits_arr[s] = 0;
							}
							else
							{
								credits_arr[s] = credits_arr[s] - curr_credits;
							}
							return;
						}
					}
				}
				flag1 = 0;
				if(this.getAttribute('name') == "1"){
					semester = 1;
				} 
				else if(this.getAttribute('name') == "2"){
					semester = 2;
				} 
				else if(this.getAttribute('name') == "3"){
					semester = 3;
				}
				else if(this.getAttribute('name') == "4"){
					semester = 4;
				} 
				else if(this.getAttribute('name') == "5"){
					semester = 5;
				} 
				else if(this.getAttribute('name') == "6"){
					semester = 6;
				} 
				else if(this.getAttribute('name') == "7"){
					semester = 7;
				} 
				else if(this.getAttribute('name') == "8"){
					semester = 8;
				} 

				for (var currSem = 1; currSem < 9; currSem++){
					if (prereq_arr[currSem].includes(draggedItem.innerHTML) && flag1 == 0)
					{
						flag1 = 1;
						var itemIndex = prereq_arr[currSem].indexOf(draggedItem.innerHTML);
						prereq_arr[currSem].splice(itemIndex, 1);
						var idx = index[currSem];
						index[currSem] = idx-1;
						var key2 = draggedItem.textContent;
		
						//Check credits
						var curr_credits = credits_list[key2];
						if(curr_credits === undefined){
							curr_credits = 3;
						}
					
						if (credits_arr[currSem] - curr_credits < 0)
						{
							credits_arr[currSem] = 0;
						}
						else
						{
							credits_arr[currSem] = credits_arr[currSem] - curr_credits;
						}
		
						console.log(credits_arr[currSem]);
						break;
					}
				}

				for(var prev = 0; prev < semester; prev++){
					var key = draggedItem.textContent; // {{c.department}} {{c.number}} - string
						for(var n in prereq_list[key]){
							for(var r in prereq_list[key][n]){
								if(prereq_arr[prev].includes(prereq_list[key][n][r])){ 
									prereqnum++;
									break;
								}
							}
						}
				}

				var key2 = draggedItem.textContent;
				countnum = 0;
				for(var p in prereq_list[key2]){
					countnum++;	
				}

				// Check credits
				var curr_credits = credits_list[key2];
				if(curr_credits === undefined){
					curr_credits = 3;
				}

				if((prereqnum >= countnum) && (credits_arr[semester]+curr_credits <= 18)){
					this.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
					this.append(draggedItem);
					var semesterName = "semester"+semester.toString();
					draggedItem.setAttribute("name",semesterName);
					
					if (!(prereq_arr[semester].includes(draggedItem.innerHTML)))
					{
						var idx = index[semester];
						prereq_arr[semester].push(draggedItem.innerHTML);
						index[semester] = idx+1;
						credits_arr[semester] = credits_arr[semester] + curr_credits;
						flag = 1;
					}
				}
				if((credits_arr[semester]+curr_credits) > 18){
					flag = 0;
					console.log("Too many credits");
				}
				if(prereqnum < countnum){
					flag = 0;
					console.log("Missing prerequisite");
				}
			}
		});
		if (flag == 1) {
			flag = 0;
			break;
		}
	}
}


