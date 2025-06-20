# Choosing the right model

> Selecting the optimal Claude model for your application involves balancing three key considerations: capabilities, speed, and cost. This guide helps you make an informed decision based on your specific requirements.

## Establish key criteria

When choosing a Claude model, we recommend first evaluating these factors:

* **Capabilities:** What specific features or capabilities will you need the model to have in order to meet your needs?
* **Speed:** How quickly does the model need to respond in your application?
* **Cost:** What's your budget for both development and production usage?

Knowing these answers in advance will make narrowing down and deciding which model to use much easier.

***

## Choose the best model to start with

There are two general approaches you can use to start testing which Claude model best works for your needs.

### Option 1: Start with a fast, cost-effective model

For many applications, starting with a faster, more cost-effective model like Claude 3.5 Haiku can be the optimal approach:

1. Begin implementation with Claude 3.5 Haiku
2. Test your use case thoroughly
3. Evaluate if performance meets your requirements
4. Upgrade only if necessary for specific capability gaps

This approach allows for quick iteration, lower development costs, and is often sufficient for many common applications. This approach is best for:

* Initial prototyping and development
* Applications with tight latency requirements
* Cost-sensitive implementations
* High-volume, straightforward tasks

### Option 2: Start with the most capable model

For complex tasks where intelligence and advanced capabilities are paramount, you may want to start with the most capable model and then consider optimizing to more efficient models down the line:

1. Implement with Claude Opus 4 or Claude Sonnet 4
2. Optimize your prompts for these models
3. Evaluate if performance meets your requirements
4. Consider increasing efficiency by downgrading intelligence over time with greater workflow optimization

This approach is best for:

* Complex reasoning tasks
* Scientific or mathematical applications
* Tasks requiring nuanced understanding
* Applications where accuracy outweighs cost considerations
* Advanced coding

## Model selection matrix

| When you need...                                                                                                        | We recommend starting with... | Example use cases                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Highest intelligence and reasoning, superior capabilities for the most complex tasks, such as multi agent coding        | Claude Opus 4                 | Multi agent frameworks, complex codebase refactoring, nuanced creative writing, complex financial or scientific analysis |
| Balance of intelligence and speed, strong performance but with faster response times                                    | Claude Sonnet 4               | Complex customer chatbot inquiries, complex code generation, straightforward agentic loops, data analysis                |
| Fast responses at lower cost, optimized for high volume, straightforward appications with no need for extended thinking | Claude 3.5 Haiku              | Basic customer support, high volume formulaic content generation, straightforward data extraction                        |

***

## Decide whether to upgrade or change models

To determine if you need to upgrade or change models, you should:

1. [Create benchmark tests](/en/docs/test-and-evaluate/develop-tests) specific to your use case - having a good evaluation set is the most important step in the process
2. Test with your actual prompts and data
3. Compare performance across models for:
   * Accuracy of responses
   * Response quality
   * Handling of edge cases
4. Weigh performance and cost tradeoffs

## Next steps

<CardGroup cols={3}>
  <Card title="Model comparison chart" icon="head-side-gear" href="/en/docs/about-claude/models/overview">
    See detailed specifications and pricing for the latest Claude models
  </Card>

  <Card title="Migrate to Claude 4" icon="sparkles" href="/en/docs/about-claude/models/migrating-to-claude-4">
    Follow the checklist for an easy migration to Claude 4
  </Card>

  <Card title="Start building" icon="code" href="/en/docs/get-started">
    Get started with your first API call
  </Card>
</CardGroup>
