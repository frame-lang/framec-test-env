@target typescript

system TSFieldsTest {

  interface:
    init()
    tick()

  machine:
    $Start {
      $>() {
        // Assign fields on this to require TS class member declarations
        this.counter = 0
        this.stateName = "Start"
        this.settings = { "verbose": true }
      }

      init() {
        this.counter = this.counter + 1
      }

      tick() {
        this.counter = this.counter + 1
      }
    }
}

