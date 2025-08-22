"""
AI Prompts Configuration
专门的AI提示词配置文件
"""

class PromptTemplates:
    """AI提示词模板类"""
    
    # 单篇文章专门总结提示词（英文版）
    SINGLE_ARTICLE_SUMMARY = """
Please create a high-quality WeChat sharing content for the following news article. Requirements:

1. Content length: {min_length}-{max_length} Chinese characters
2. Deeply analyze the article's key points and extract core information and value
3. Use vivid and engaging language suitable for social media sharing
4. Add relevant perspectives or impact analysis
5. Use appropriate emoji symbols to enhance expression
6. Clear structure: Title highlights + Core content + Impact analysis
7. End with "Read original article" guidance
8. Response must be in Chinese

Content structure should include:
- 📰 Attractive headline summary
- 💡 Core content analysis (main points, significance)
- 🔍 Impact analysis or thought-provoking insights
- 🔗 Link to original article

Article information:
Title: {title}
Content: {content}
Link: {link}

Please generate professional and attractive WeChat sharing content in Chinese:
"""

    # 多篇文章汇总提示词
    MULTIPLE_ARTICLES_SUMMARY = """
Please summarize the following news articles into a WeChat message suitable for sharing. Requirements:

1. Total length: {min_length}-{max_length} Chinese characters
2. Highlight important news with concise and clear language
3. Maintain objective and neutral tone
4. Include "View details" prompt at the end
5. Use appropriate emoji symbols for readability
6. Response must be in Chinese

News content:
{articles_text}

Please generate a WeChat message in Chinese:
"""

    # 文章分类提示词
    ARTICLE_CLASSIFICATION = """
Analyze the content and categorize it into exactly one of these categories:
Technology, Development, Entertainment, Finance, Health, Politics, Other

Classification requirements:
- Choose the SINGLE most appropriate category based on:
  * Primary topic and main focus of the content
  * Key terminology and concepts used
  * Target audience and purpose
  * Technical depth and complexity level
- For content that could fit multiple categories:
  * Identify the dominant theme
  * Consider the most specific applicable category
  * Use the primary intended purpose
- If content appears ambiguous:
  * Focus on the most prominent aspects
  * Consider the practical application
  * Choose the category that best serves user needs

Output format:
Return ONLY the category name, no other text or explanation.
Must be one of the provided categories exactly as written.
"""

    # 文章标签生成提示词
    ARTICLE_TAGS = """
Analyze the content and add appropriate tags based on:
- Main topics and themes
- Key concepts and terminology 
- Target audience and purpose
- Technical depth and domain
- 2-4 tags are enough

Output format:
Return a list of tags, separated by commas, no other text or explanation.
e.g. "AI, Technology, Innovation, Future"
"""

    # 文章评分提示词
    ARTICLE_SCORING = """
Please give a score between 0 and 10 based on the following content.
Evaluate the content comprehensively considering clarity, accuracy, depth, logical structure, language expression, and completeness.
Note: If the content is an article or a text intended to be detailed, the length is an important factor. Generally, content under 300 words may receive a lower score due to lack of substance, unless its type (such as poetry or summary) is inherently suitable for brevity.

Output format:
Return the score (0-10), no other text or explanation.
E.g. "8", "5", "3", etc.
"""

    # 孔子评论提示词
    CONFUCIUS_COMMENT = """
Please act as Confucius and write a 100-word comment on the article.
Content needs to be in line with the Chinese mainland's regulations.

Output format:
Return the comment only, no other text or explanation.
Reply short and concise, 100 words is enough.
Response must be in Chinese.
"""

    # 详细总结提示词
    DETAILED_SUMMARY = """
Please read the article carefully and summarize its core content in the format of [Choice: Key Point List / Concise Paragraph]. The summary should clearly cover:

1. What is the main topic/theme of the article?
2. What key arguments/main information did the author put forward?
3. (Optional, if the article contains) What important data, cases, or examples are there?
4. What main conclusions did the article reach or what core information did it ultimately convey?

Strive for comprehensive, accurate, and concise.
Response must be in Chinese.
"""

    # 系统角色定义
    SYSTEM_ROLES = {
        "content_strategist": "You are a professional content strategist who excels at transforming news content into valuable and insightful social media content. You need to deeply analyze the core value of news and provide unique insights and thinking perspectives.",
        "news_summarizer": "You are a professional news summarization assistant who excels at summarizing news content into concise and readable WeChat messages.",
        "content_analyst": "You are a professional content analyst who can accurately categorize and evaluate article content.",
        "confucius": "You are Confucius, the great Chinese philosopher and educator. You will comment on modern events from your perspective of wisdom and moral philosophy."
    }

    @classmethod
    def get_single_article_prompt(cls, title: str, content: str, link: str, min_length: int, max_length: int) -> str:
        """获取单篇文章总结提示词"""
        return cls.SINGLE_ARTICLE_SUMMARY.format(
            title=title,
            content=content,
            link=link,
            min_length=min_length,
            max_length=max_length
        )
    
    @classmethod
    def get_multiple_articles_prompt(cls, articles_text: str, min_length: int, max_length: int) -> str:
        """获取多篇文章汇总提示词"""
        return cls.MULTIPLE_ARTICLES_SUMMARY.format(
            articles_text=articles_text,
            min_length=min_length,
            max_length=max_length
        )
    
    @classmethod
    def get_system_role(cls, role_type: str) -> str:
        """获取系统角色定义"""
        return cls.SYSTEM_ROLES.get(role_type, cls.SYSTEM_ROLES["content_strategist"])
