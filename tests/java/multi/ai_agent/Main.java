// Multi-source port of demos/33_ai_agent.fjava.

public class Main {
    public static void main(String[] args) {
        Agent agent = new Agent();
        agent.tool_runner.set_parent(agent);

        String s1 = (String) agent.status();
        if (!"idle".equals(s1)) {
            throw new RuntimeException("Expected idle, got " + s1);
        }

        agent.task("Add validation");
        agent.approve();

        String s2 = (String) agent.status();
        if (!"complete".equals(s2)) {
            throw new RuntimeException("Expected complete, got " + s2);
        }

        System.out.println("PASS: ai_agent");
    }
}
