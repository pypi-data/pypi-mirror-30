## benchit - Quick n' Easy Python Benchmarking

Quickly find where your code is spending its time.

[![Build Status](https://secure.travis-ci.org/scuml/benchit.png?branch=master)](http://travis-ci.org/scuml/benchit)

Benchit is intended to be a minimalistic library that times how long it takes to get from point A to point B.  It helps detect unoptimized code.

Benchit is only compatible with python 3.  For python 2 support, use benchit==0.2.6 (https://pypi.python.org/pypi/bench-it/0.2.6)

### Installation

    pip install bench-it

### Example

    from benchit import BenchIt
    from time import sleep


    def demo_benchmark():
        b = BenchIt()  # starts the timer

        # do stuff
        sleep(1); b()  # Add marker after this code.  Code used as marker name.

        sleep(.2);
        sleep(.3);
        sleep(.4);
        b("More stuff done")  # Add a custom named marker

        for i in range(1, 5):
          sleep(.1); b()  # Code can be marked in a loop

        b.display()  # Display output as a table


    demo_benchmark()


    BenchIt
    +-----------------+----------------+------------+------+----------+---------+---------+
    | Marker          | Method         |       Line | Hits | Avg Time | Runtime | Percent |
    +-----------------+----------------+------------+------+----------+---------+---------+
    | sleep(1)        | demo_benchmark |  demo.py:9 |    1 |  1.01341 | 1.01341 |   43.33 |
    | More stuff Done | demo_benchmark | demo.py:14 |    1 |  0.91278 | 0.91278 |   39.03 |
    | sleep(.1)       | demo_benchmark | demo.py:17 |    4 |  0.10306 | 0.41223 |   17.63 |
    +-----------------+----------------+------------+------+----------+---------+---------+
    Total runtime: 2.33860

### How to Use

Instantiating the class starts the timer.  BenchIt is run as a singleton.  Re-instantiating anywhere in your code will pull in the previously instantiated timer.  To create a new timer, initialize BenchIt with a unique name.

    b = BenchIt()

    b2 = BenchIt()  # b == b2

    b3 = BenchIt("Timer A")  # b != b3


Set a marker after some code.

    call_a_method(); b()  # Quickly add a marker after a method

    method1()
    method2()
    b("Two methods called")  # Or create a manual marker after a chunk of code

Stop and display the table for analysis.

    b.display()

### Methods

`benchit.__init__()` Instantiate and start the timer.

`benchit.__call__(marker_name)` Add marker at this point.

`benchit.stop()` Optionally, stop the timer at a point.

`benchit.display()` Display the table.  Stops the timer if running.


### Credits
* Special thanks Luke Maurits for [prettytable](https://pypi.python.org/pypi/PrettyTable)*