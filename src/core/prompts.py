"""
AI Prompts Configuration
专门的AI提示词配置文件
"""


class PromptTemplates:
    """AI提示词模板类"""

    # 单篇文章专门总结提示词
    SINGLE_ARTICLE_SUMMARY = """
Please create a high-quality WeChat sharing content for the following news article. Requirements:

1. **IMPORTANT: If the original article is in a non-Chinese language (English, etc.), you must first translate it to Chinese, then create the summary based on the Chinese translation.**
2. Content length: {min_length}-{max_length} Chinese characters
3. Deeply analyze the article's key points and extract core information and value
4. Use vivid and engaging language suitable for social media sharing
5. Add relevant perspectives or impact analysis
6. Use appropriate emoji symbols to enhance expression
7. Clear structure: Title highlights + Core content + Impact analysis
8. End with "阅读原文" (Read original article) guidance
9. **The final output must be entirely in Chinese**

Content structure should include:
- 📰 Attractive headline summary (in Chinese)
- 💡 Core content analysis (main points, significance) (in Chinese)
- 🔍 Impact analysis or thought-provoking insights (in Chinese)
- 🔗 Link to original article with Chinese prompt

Article information:
Title: {title}
Content: {content}
Link: {link}

Please generate professional and attractive WeChat sharing content entirely in Chinese:
"""

    # 多篇文章汇总提示词
    MULTIPLE_ARTICLES_SUMMARY = """
Please summarize the following news articles into a WeChat message suitable for sharing. Requirements:

1. **IMPORTANT: If any articles are in non-Chinese languages, first translate them to Chinese, then create the summary.**
2. Total length: {min_length}-{max_length} Chinese characters
3. Highlight important news with concise and clear language
4. Maintain objective and neutral tone
5. Include "查看详情" (View details) prompt at the end
6. Use appropriate emoji symbols for readability
7. **The final output must be entirely in Chinese**

News content:
{articles_text}

Please generate a WeChat message entirely in Chinese:
"""

    # 文章分类提示词
    ARTICLE_CLASSIFICATION = """
Analyze the content and categorize it into exactly one of these categories (respond in Chinese):
科技 (Technology), 开发 (Development), 娱乐 (Entertainment), 金融 (Finance), 健康 (Health), 政治 (Politics), 其他 (Other)

Classification requirements:
- If the content is in a non-Chinese language, understand it first, then classify
- Choose the SINGLE most appropriate category based on:
  * Primary topic and main focus of the content
  * Key terminology and concepts used
  * Target audience and purpose
  * Technical depth and complexity level
- For content that could fit multiple categories:
  * Identify the dominant theme
  * Consider the most specific applicable category
  * Use the primary intended purpose

Output format:
Return ONLY the Chinese category name, no other text or explanation.
Must be one of: 科技, 开发, 娱乐, 金融, 健康, 政治, 其他
"""

    # 文章标签生成提示词
    ARTICLE_TAGS = """
Analyze the content and add appropriate tags in Chinese based on:
- If content is in non-Chinese language, understand it first
- Main topics and themes
- Key concepts and terminology
- Target audience and purpose
- Technical depth and domain
- 2-4 tags are enough

Output format:
Return a list of Chinese tags, separated by commas, no other text or explanation.
Example: "人工智能, 科技, 创新, 未来"
"""

    # 文章评分提示词
    ARTICLE_SCORING = """
Please give a score between 0 and 10 based on the following content.
- If content is in non-Chinese language, understand it first before scoring
- Evaluate the content comprehensively considering clarity, accuracy, depth, logical structure, language expression, and completeness
- Note: If the content is an article or detailed text, length is an important factor. Generally, content under 300 words may receive a lower score due to lack of substance, unless its type (such as poetry or summary) is inherently suitable for brevity

Output format:
Return only the score (0-10), no other text or explanation.
Examples: "8", "5", "3", etc.
"""

    # 孔子评论提示词
    CONFUCIUS_COMMENT = """
Please act as Confucius and write a 100-word comment on the article in Chinese.
- If the original content is in non-Chinese language, understand it first
- Content needs to be in line with Chinese mainland's regulations
- Write from Confucius's perspective of wisdom and moral philosophy
- Keep it appropriate for modern context

Output format:
Return the comment only in Chinese, no other text or explanation.
Reply should be concise, around 100 Chinese characters.
"""

    # 详细总结提示词
    DETAILED_SUMMARY = """
Please read the article carefully and summarize its core content. Requirements:

1. **IMPORTANT: If the original article is in non-Chinese language, first understand it, then provide summary in Chinese**
2. The summary should clearly cover:
   - What is the main topic/theme of the article?
   - What key arguments/main information did the author present?
   - (Optional, if applicable) What important data, cases, or examples are there?
   - What main conclusions did the article reach or what core information did it ultimately convey?

3. Strive for comprehensive, accurate, and concise
4. **Output must be entirely in Chinese**
5. Format: [Choice: Key Point List / Concise Paragraph]

Please provide the summary in Chinese:
"""

    # 系统角色定义
    SYSTEM_ROLES = {
        "content_strategist": "You are a professional content strategist who excels at transforming news content into valuable and insightful social media content. You can understand content in any language and always provide Chinese output. You need to deeply analyze the core value of news and provide unique insights and thinking perspectives.",
        "news_summarizer": "You are a professional news summarization assistant who excels at summarizing news content into concise and readable WeChat messages. You can process content in any language and always output in Chinese.",
        "content_analyst": "You are a professional content analyst who can accurately categorize and evaluate article content in any language. You always provide responses in Chinese when required.",
        "confucius": "You are Confucius, the great Chinese philosopher and educator. You will comment on modern events from your perspective of wisdom and moral philosophy. You can understand content in any language but always respond in Chinese.",
    }

    @classmethod
    def get_single_article_prompt(
        cls, title: str, content: str, link: str, min_length: int, max_length: int
    ) -> str:
        """获取单篇文章总结提示词"""
        return cls.SINGLE_ARTICLE_SUMMARY.format(
            title=title,
            content=content,
            link=link,
            min_length=min_length,
            max_length=max_length,
        )

    @classmethod
    def get_multiple_articles_prompt(
        cls, articles_text: str, min_length: int, max_length: int
    ) -> str:
        """获取多篇文章汇总提示词"""
        return cls.MULTIPLE_ARTICLES_SUMMARY.format(
            articles_text=articles_text, min_length=min_length, max_length=max_length
        )

    @classmethod
    def get_system_role(cls, role_type: str) -> str:
        """获取系统角色定义"""
        return cls.SYSTEM_ROLES.get(role_type, cls.SYSTEM_ROLES["content_strategist"])
