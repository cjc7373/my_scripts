// Code for: https://play.elevatorsaga.com/
// STATUS: Abandoned
{
    init: function(elevators, floors) {
        var max_floor = floors.length - 1;
        var min_pressed_floor = max_floor + 1;
        var max_pressed_floor = -1;
        var elevator = elevators[0]; // Let's use the first elevator

        // let schedule_an_idle_elevator = (floor) => {
        //     for (e of elevators) {
        //         if (e.state == 'idle') {
        //             e.goToFloor(floorNum);
        //             if (floorNum < e.currentFloor) {
        //                 e.state = 'down';
        //             } else {
        //                 e.state = 'up';
        //             }
        //             return true;
        //         }
        //     }
        //     return false;
        // }

        for (e of elevators) {
            e.on("idle", function () {
                e.goToFloor(Math.round(max_floor / 2));
                e.state = 'idle';
            })
        }

        for (floor of floors) {
            console.log(floor);
            floor.on("up_button_pressed", function() {
                elevator.goToFloor(floor.floorNum());
                console.log("up_button_pressed", floor.floorNum());
            });

            floor.on("down_button_pressed", function () {
                elevator.goToFloor(floor.floorNum());
                console.log("down_button_pressed", floor.floorNum());
            });
            console.log('done');
        }

        elevator.on("floor_button_pressed", function(floorNum) {
            // elevator.goToFloor(floorNum);
            // console.log("Going to floor", floorNum);
            console.log("current queue is ", elevator.getPressedFloors())
        })


    },
    update: function(dt, elevators, floors) {
        // We normally don't need to do anything here
    }
}