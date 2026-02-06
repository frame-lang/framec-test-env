@@target rust

@@system Scope {
    interface:
        run()

    machine:
        $Start {
            run() {
                // Rust doesn't support nested functions, use a closure instead
                let helper = || {
                    let y = 5;
                    println!("{}", y);
                };
                helper();
                let y = 10;
                println!("{}", y);
            }
        }
    }
}
