// Multi-source port of demos/29_game_level.fjava.

public class Main {
    public static void main(String[] args) {
        GameLevel level = new GameLevel();
        int failures = 0;

        if (!level.level_status().equals("loading")) {
            System.out.println("FAIL: initial status expected loading");
            failures++;
        }

        level.start();
        if (!level.level_status().equals("playing")) {
            System.out.println("FAIL: status after start expected playing");
            failures++;
        }

        for (int i = 0; i < 3; i++) {
            String r = level.spawn_enemy();
            if (!r.equals("enemy_spawned")) {
                System.out.println("FAIL: spawn " + (i + 1) + " expected enemy_spawned");
                failures++;
            }
        }

        String r = level.spawn_enemy();
        if (!r.equals("no_more_enemies")) {
            System.out.println("FAIL: spawn after exhausted expected no_more_enemies");
            failures++;
        }

        level.complete();
        if (!level.level_status().equals("victory")) {
            System.out.println("FAIL: status after complete expected victory");
            failures++;
        }

        if (failures > 0) {
            System.out.println("FAIL: game_level (" + failures + " failures)");
            System.exit(1);
        }
        System.out.println("PASS: game_level");
    }
}
