@@target typescript

@@system TSAdapterHelpersTest {

  interface:
    start()

  machine:
    $Idle {
      start() {
        // Use adapter runtime helper functions (must be declared in d.ts)
        var ts = frameRuntimeGetTimestamp()
        frameRuntimeSetEnv("TEST_KEY", "TEST_VALUE")
        this.lastTs = ts
      }
    }
}

