@@target c

fn test_forward_block_comment_across_lines() {
    // Test: transition
=> $^ /* start
           still comment
           */
    print("SUCCESS: test_forward_block_comment_across_lines completed")
}

fn main() {
    test_forward_block_comment_across_lines()
}
