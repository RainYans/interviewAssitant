# scripts/init_questions_data.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import user, profile, resume, question  # 导入所有模型
from app.models.question import Question, QuestionCategory  # 然后再导入具体类
import json
def init_categories(db: Session):
    """初始化分类数据"""
    categories_data = [
        {
            "name": "前端开发",
            "description": "包括HTML/CSS、JavaScript、Vue、React等前端技术",
            "icon": "Monitor",
            "sort_order": 1
        },
        {
            "name": "后端开发", 
            "description": "包括Java、Python、Node.js、数据库等后端技术",
            "icon": "DataAnalysis",
            "sort_order": 2
        },
        {
            "name": "算法数据结构",
            "description": "编程算法、数据结构、系统设计等",
            "icon": "Notebook", 
            "sort_order": 3
        },
        {
            "name": "通用问题",
            "description": "项目经验、团队协作、职业规划等通用面试问题",
            "icon": "Briefcase",
            "sort_order": 4
        }
    ]
    
    for cat_data in categories_data:
        existing = db.query(QuestionCategory).filter(
            QuestionCategory.name == cat_data["name"]
        ).first()
        
        if not existing:
            category = QuestionCategory(**cat_data)
            db.add(category)
    
    db.commit()
    print("✅ 分类数据初始化完成")

def init_questions(db: Session):
    """初始化题目数据"""
    questions_data = [
        # === 前端开发题目 ===
        {
            "title": "Vue3 相比 Vue2 有哪些重要更新？",
            "description": "这是一道考察对Vue框架发展和新特性理解的题目。面试官希望了解候选人是否关注技术发展，以及对新技术的理解深度。",
            "category": "前端开发",
            "sub_category": "Vue.js",
            "difficulty": "中等",
            "tags": json.dumps(["Vue.js", "前端框架", "技术更新"]),
            "answer": """Vue3 相比 Vue2 的重要更新包括：<br>
1. <strong>性能提升</strong>：重写了虚拟DOM，更新性能提升1.3~2倍<br>
2. <strong>Composition API</strong>：提供了更灵活的代码组织方式<br>
3. <strong>TypeScript支持</strong>：源码使用TypeScript重写，提供更好的类型推导<br>
4. <strong>Tree-shaking</strong>：更小的打包体积<br>
5. <strong>Fragment</strong>：支持多个根节点<br>
6. <strong>Teleport</strong>：可以将组件渲染到DOM树的其他位置<br>
7. <strong>Suspense</strong>：异步组件的新方式""",
            "key_points": json.dumps([
                "重点说明性能优化的具体表现",
                "解释Composition API解决的问题", 
                "结合实际项目经验举例说明",
                "对比Options API的优劣"
            ]),
            "related_topics": json.dumps(["Proxy vs Object.defineProperty", "Vue3 响应式原理", "setup函数"]),
            "interviewer_perspective": "考察候选人对前端框架发展的关注度，以及是否有实际使用经验。优秀的候选人会结合具体场景说明各特性的应用。",
            "views": 2341,
            "stars": 189,
            "is_featured": True
        },
        {
            "title": "如何实现前端性能优化？",
            "description": "这是一道综合性很强的题目，考察候选人对前端性能优化的全面理解和实践经验。",
            "category": "前端开发",
            "sub_category": "性能优化",
            "difficulty": "困难",
            "tags": json.dumps(["性能优化", "工程化", "最佳实践"]),
            "answer": """前端性能优化可以从以下几个方面进行：<br>
1. <strong>加载性能优化</strong><br>
   - 代码分割和懒加载<br>
   - 资源压缩（gzip、图片压缩）<br>
   - CDN加速<br>
   - HTTP缓存策略<br>
2. <strong>渲染性能优化</strong><br>
   - 减少重排重绘<br>
   - 使用CSS3动画代替JS动画<br>
   - 虚拟滚动<br>
3. <strong>代码层面优化</strong><br>
   - 防抖节流<br>
   - Web Worker处理复杂计算<br>
   - 避免内存泄漏""",
            "key_points": json.dumps([
                "从加载、渲染、代码三个维度展开",
                "每个优化点都给出具体实施方案",
                "结合性能监控工具说明优化效果",
                "提及最新的优化技术如Web Vitals"
            ]),
            "related_topics": json.dumps(["Lighthouse", "Web Vitals", "Performance API"]),
            "interviewer_perspective": "希望候选人不仅知道优化方法，更要理解背后的原理。能够根据实际场景选择合适的优化策略，并量化优化效果。",
            "views": 3456,
            "stars": 267,
            "is_featured": True
        },
        {
            "title": "什么是虚拟DOM？它的优势是什么？",
            "description": "考察对虚拟DOM概念和原理的理解。",
            "category": "前端开发",
            "sub_category": "JavaScript",
            "difficulty": "中等",
            "tags": json.dumps(["虚拟DOM", "React", "Vue", "性能优化"]),
            "answer": """虚拟DOM（Virtual DOM）是真实DOM的JavaScript对象表示。<br><br>
<strong>主要优势：</strong><br>
1. <strong>性能优化</strong>：减少真实DOM操作，通过diff算法最小化更新<br>
2. <strong>跨浏览器兼容</strong>：抽象了浏览器差异<br>
3. <strong>批量更新</strong>：可以批量处理DOM变更<br>
4. <strong>可预测性</strong>：函数式编程思想，易于调试<br><br>
<strong>工作原理：</strong><br>
1. 状态改变时创建新的虚拟DOM树<br>
2. 与旧的虚拟DOM树进行对比（diff）<br>
3. 计算出最小变更集合<br>
4. 将变更应用到真实DOM（patch）""",
            "key_points": json.dumps([
                "准确解释虚拟DOM的概念",
                "说明性能优化的具体体现",
                "介绍diff算法的基本思想",
                "对比直接操作DOM的劣势"
            ]),
            "related_topics": json.dumps(["Diff算法", "React Fiber", "Vue响应式系统"]),
            "interviewer_perspective": "考察对前端框架核心概念的理解，以及性能优化意识。",
            "views": 1890,
            "stars": 156
        },
        {
            "title": "CSS中的BFC是什么？如何触发？",
            "description": "CSS盒模型和布局相关的重要概念。",
            "category": "前端开发",
            "sub_category": "CSS",
            "difficulty": "中等",
            "tags": json.dumps(["CSS", "BFC", "布局", "盒模型"]),
            "answer": """BFC（Block Formatting Context）块级格式化上下文是CSS布局的重要概念。<br><br>
<strong>BFC的特性：</strong><br>
1. 内部块级盒子垂直排列<br>
2. 同一BFC内相邻块级元素的margin会合并<br>
3. BFC区域不会与浮动元素重叠<br>
4. 计算BFC高度时，浮动子元素也参与计算<br><br>
<strong>触发BFC的方法：</strong><br>
1. 根元素html<br>
2. float值不为none<br>
3. position为absolute或fixed<br>
4. display为inline-block、table-cell、flex等<br>
5. overflow值不为visible<br><br>
<strong>应用场景：</strong><br>
- 清除浮动<br>
- 防止margin重叠<br>
- 两栏自适应布局""",
            "key_points": json.dumps([
                "清楚解释BFC的概念和特性",
                "列举触发BFC的条件",
                "结合实际应用场景说明",
                "能够解决相关的布局问题"
            ]),
            "related_topics": json.dumps(["IFC", "清除浮动", "margin重叠"]),
            "interviewer_perspective": "考察CSS基础知识的掌握程度，以及解决布局问题的能力。",
            "views": 1234,
            "stars": 98
        },
        {
            "title": "React和Vue的区别是什么？",
            "description": "前端框架对比类题目，考察对主流框架的理解。",
            "category": "前端开发", 
            "sub_category": "框架对比",
            "difficulty": "中等",
            "tags": json.dumps(["React", "Vue.js", "框架对比"]),
            "answer": """React和Vue的主要区别：<br>
1. <strong>设计理念</strong><br>
   - React：函数式编程思想，单向数据流<br>
   - Vue：渐进式框架，双向数据绑定<br>
2. <strong>模板语法</strong><br>
   - React：JSX语法<br>
   - Vue：模板语法，更接近HTML<br>
3. <strong>学习曲线</strong><br>
   - React：相对陡峭，需要掌握JSX、状态管理等<br>
   - Vue：更平缓，API设计更直观<br>
4. <strong>生态系统</strong><br>
   - React：更庞大的社区和生态<br>
   - Vue：官方维护的配套工具更完整""",
            "key_points": json.dumps([
                "从技术特点、使用场景、生态等多角度对比",
                "结合实际项目选择框架的考虑因素",
                "避免绝对化的评价，强调适合的场景"
            ]),
            "related_topics": json.dumps(["Virtual DOM", "状态管理", "组件化开发"]),
            "interviewer_perspective": "考察对主流框架的理解深度，以及技术选型的思考能力。",
            "views": 1876,
            "stars": 145
        },
        {
            "title": "说说JavaScript闭包的理解和应用？",
            "description": "JavaScript基础概念题，闭包是面试的经典话题。",
            "category": "前端开发",
            "sub_category": "JavaScript",
            "difficulty": "中等", 
            "tags": json.dumps(["JavaScript", "闭包", "作用域"]),
            "answer": """闭包是指有权访问另一个函数作用域中变量的函数。<br>
<strong>产生原因：</strong><br>
- 函数嵌套<br>
- 内部函数引用外部函数的变量<br>
- 外部函数返回内部函数<br><br>
<strong>常见应用：</strong><br>
1. <strong>数据私有化</strong><br>
2. <strong>函数工厂</strong><br>
3. <strong>事件处理程序</strong><br>
4. <strong>模块化开发</strong><br><br>
<strong>注意事项：</strong><br>
- 可能造成内存泄漏<br>
- 合理使用，避免滥用""",
            "key_points": json.dumps([
                "准确解释闭包的概念和形成条件",
                "结合代码示例说明",
                "说明实际应用场景",
                "提及性能注意事项"
            ]),
            "related_topics": json.dumps(["作用域链", "垃圾回收", "内存管理"]),
            "interviewer_perspective": "闭包是JavaScript的核心概念，考察对语言特性的深入理解。",
            "views": 2156,
            "stars": 198
        },
        {
            "title": "ES6有哪些新特性？",
            "description": "JavaScript ES6新特性相关问题。",
            "category": "前端开发",
            "sub_category": "JavaScript",
            "difficulty": "简单",
            "tags": json.dumps(["ES6", "JavaScript", "新特性"]),
            "answer": """ES6（ES2015）的主要新特性：<br><br>
<strong>1. 变量声明</strong><br>
- let和const：块级作用域，不存在变量提升<br>
- const：声明常量，不可重复赋值<br><br>
<strong>2. 箭头函数</strong><br>
- 简化函数语法<br>
- 不绑定this，继承外层作用域<br><br>
<strong>3. 模板字符串</strong><br>
- 支持变量插值：`${variable}`<br>
- 支持多行字符串<br><br>
<strong>4. 解构赋值</strong><br>
- 数组解构：[a, b] = [1, 2]<br>
- 对象解构：{name, age} = person<br><br>
<strong>5. 类和继承</strong><br>
- class关键字定义类<br>
- extends实现继承<br><br>
<strong>6. 模块化</strong><br>
- import/export语法<br>
- 原生模块支持""",
            "key_points": json.dumps([
                "列举主要的ES6特性",
                "说明每个特性解决的问题",
                "结合代码示例说明用法",
                "提及浏览器兼容性问题"
            ]),
            "related_topics": json.dumps(["Babel", "ES6模块", "Promise", "Set和Map"]),
            "interviewer_perspective": "考察对JavaScript语言发展的了解，以及新特性的掌握程度。",
            "views": 2890,
            "stars": 245
        },
        {
            "title": "Promise的理解和使用？",
            "description": "异步编程的重要概念。",
            "category": "前端开发",
            "sub_category": "JavaScript",
            "difficulty": "中等",
            "tags": json.dumps(["Promise", "异步编程", "JavaScript"]),
            "answer": """Promise是异步编程的解决方案，代表一个异步操作的最终完成或失败。<br><br>
<strong>三种状态：</strong><br>
1. <strong>Pending</strong>：初始状态，既不是成功也不是失败<br>
2. <strong>Fulfilled</strong>：操作成功完成<br>
3. <strong>Rejected</strong>：操作失败<br><br>
<strong>基本用法：</strong><br>
```javascript
const promise = new Promise((resolve, reject) => {
  // 异步操作
  if (success) {
    resolve(result);
  } else {
    reject(error);
  }
});
```<br><br>
<strong>常用方法：</strong><br>
- then()：处理成功的回调<br>
- catch()：处理失败的回调<br>
- finally()：无论成功失败都会执行<br>
- Promise.all()：等待所有Promise完成<br>
- Promise.race()：等待第一个Promise完成""",
            "key_points": json.dumps([
                "解释Promise的三种状态",
                "说明Promise解决的问题（回调地狱）",
                "掌握常用API的使用",
                "理解Promise链式调用"
            ]),
            "related_topics": json.dumps(["async/await", "回调地狱", "事件循环"]),
            "interviewer_perspective": "Promise是现代JavaScript异步编程的基础，考察异步编程思维。",
            "views": 3210,
            "stars": 278
        },

        # === 后端开发题目 ===
        {
            "title": "Spring Boot的核心特性有哪些？",
            "description": "Java后端开发框架相关问题。",
            "category": "后端开发",
            "sub_category": "Spring",
            "difficulty": "中等",
            "tags": json.dumps(["Java", "Spring Boot", "后端框架"]),
            "answer": """Spring Boot的核心特性包括：<br>
1. <strong>自动配置</strong><br>
   - 根据classpath自动配置Spring应用<br>
   - 减少样板代码<br>
2. <strong>起步依赖</strong><br>
   - 预定义的依赖组合<br>
   - 简化Maven/Gradle配置<br>
3. <strong>内嵌服务器</strong><br>
   - 内置Tomcat、Jetty等<br>
   - 可独立运行的jar包<br>
4. <strong>健康检查</strong><br>
   - Actuator提供监控端点<br>
   - 生产就绪功能""",
            "key_points": json.dumps([
                "重点说明自动配置的原理",
                "对比传统Spring配置的优势",
                "结合项目实践说明使用经验"
            ]),
            "related_topics": json.dumps(["Spring Framework", "微服务", "依赖注入"]),
            "interviewer_perspective": "考察对Spring生态的掌握程度，以及实际项目开发经验。",
            "views": 1654,
            "stars": 123
        },
        {
            "title": "RESTful API设计原则是什么？",
            "description": "API设计相关的重要概念。",
            "category": "后端开发",
            "sub_category": "API设计",
            "difficulty": "中等",
            "tags": json.dumps(["RESTful", "API设计", "HTTP"]),
            "answer": """RESTful API设计原则：<br><br>
<strong>1. 资源导向</strong><br>
- URL表示资源，不是动作<br>
- 使用名词，避免动词<br>
- 例：/users/123 而不是 /getUser?id=123<br><br>
<strong>2. HTTP方法</strong><br>
- GET：获取资源<br>
- POST：创建资源<br>
- PUT：更新整个资源<br>
- PATCH：部分更新资源<br>
- DELETE：删除资源<br><br>
<strong>3. 状态码</strong><br>
- 200：成功<br>
- 201：创建成功<br>
- 400：客户端错误<br>
- 401：未授权<br>
- 404：资源不存在<br>
- 500：服务器错误<br><br>
<strong>4. 无状态</strong><br>
- 每个请求都包含完整信息<br>
- 服务器不保存客户端状态""",
            "key_points": json.dumps([
                "理解REST的核心理念",
                "掌握HTTP方法的正确使用",
                "合理使用HTTP状态码",
                "设计清晰的URL结构"
            ]),
            "related_topics": json.dumps(["HTTP协议", "API版本控制", "接口文档"]),
            "interviewer_perspective": "考察API设计能力和对HTTP协议的理解。",
            "views": 2100,
            "stars": 180
        },
        {
            "title": "数据库索引的原理和优化？",
            "description": "数据库性能优化的重要概念。",
            "category": "后端开发",
            "sub_category": "数据库",
            "difficulty": "困难",
            "tags": json.dumps(["数据库", "索引", "性能优化", "MySQL"]),
            "answer": """数据库索引是提高查询性能的重要手段。<br><br>
<strong>索引原理：</strong><br>
1. <strong>B+树结构</strong>：大多数数据库使用B+树实现索引<br>
2. <strong>减少IO次数</strong>：通过索引快速定位数据位置<br>
3. <strong>有序存储</strong>：索引按照排序规则存储<br><br>
<strong>索引类型：</strong><br>
1. <strong>主键索引</strong>：唯一且不为空<br>
2. <strong>唯一索引</strong>：保证数据唯一性<br>
3. <strong>普通索引</strong>：提高查询效率<br>
4. <strong>复合索引</strong>：多列组合索引<br>
5. <strong>覆盖索引</strong>：索引包含查询所需的所有列<br><br>
<strong>优化策略：</strong><br>
- 选择性高的列建索引<br>
- 避免在小表上建索引<br>
- 定期分析和重建索引<br>
- 遵循最左前缀原则""",
            "key_points": json.dumps([
                "理解索引的底层实现原理",
                "掌握不同类型索引的使用场景",
                "了解索引对性能的影响",
                "掌握索引优化的方法"
            ]),
            "related_topics": json.dumps(["B+树", "查询优化", "SQL调优"]),
            "interviewer_perspective": "考察数据库底层原理的理解和性能优化能力。",
            "views": 1890,
            "stars": 167
        },

        # === 算法数据结构题目 ===
        {
            "title": "常见排序算法的时间复杂度和特点？",
            "description": "基础算法知识考察。",
            "category": "算法数据结构",
            "sub_category": "排序算法",
            "difficulty": "中等",
            "tags": json.dumps(["排序算法", "时间复杂度", "算法"]),
            "answer": """常见排序算法对比：<br><br>
<strong>1. 冒泡排序</strong><br>
- 时间复杂度：O(n²)<br>
- 空间复杂度：O(1)<br>
- 稳定性：稳定<br><br>
<strong>2. 选择排序</strong><br>
- 时间复杂度：O(n²)<br>
- 空间复杂度：O(1)<br>
- 稳定性：不稳定<br><br>
<strong>3. 插入排序</strong><br>
- 时间复杂度：O(n²)<br>
- 空间复杂度：O(1)<br>
- 稳定性：稳定<br>
- 适用于小规模数据<br><br>
<strong>4. 快速排序</strong><br>
- 时间复杂度：平均O(nlogn)，最坏O(n²)<br>
- 空间复杂度：O(logn)<br>
- 稳定性：不稳定<br><br>
<strong>5. 归并排序</strong><br>
- 时间复杂度：O(nlogn)<br>
- 空间复杂度：O(n)<br>
- 稳定性：稳定""",
            "key_points": json.dumps([
                "掌握各种排序算法的实现",
                "理解时间和空间复杂度",
                "了解算法的适用场景",
                "能够根据需求选择合适的排序算法"
            ]),
            "related_topics": json.dumps(["时间复杂度", "空间复杂度", "算法稳定性"]),
            "interviewer_perspective": "考察算法基础知识和分析问题的能力。",
            "views": 2567,
            "stars": 234
        },
        {
            "title": "二叉树的遍历方式有哪些？",
            "description": "数据结构基础知识。",
            "category": "算法数据结构",
            "sub_category": "二叉树",
            "difficulty": "简单",
            "tags": json.dumps(["二叉树", "遍历", "递归"]),
            "answer": """二叉树的遍历方式：<br><br>
<strong>1. 前序遍历（根左右）</strong><br>
- 访问根节点<br>
- 前序遍历左子树<br>
- 前序遍历右子树<br><br>
<strong>2. 中序遍历（左根右）</strong><br>
- 中序遍历左子树<br>
- 访问根节点<br>
- 中序遍历右子树<br>
- 对于二叉搜索树，中序遍历得到有序序列<br><br>
<strong>3. 后序遍历（左右根）</strong><br>
- 后序遍历左子树<br>
- 后序遍历右子树<br>
- 访问根节点<br><br>
<strong>4. 层序遍历</strong><br>
- 按层从左到右访问节点<br>
- 使用队列实现<br><br>
<strong>实现方式：</strong><br>
- 递归实现：代码简洁<br>
- 迭代实现：使用栈/队列""",
            "key_points": json.dumps([
                "理解四种遍历方式的顺序",
                "掌握递归和迭代两种实现",
                "了解不同遍历的应用场景",
                "能够手写遍历代码"
            ]),
            "related_topics": json.dumps(["递归", "栈和队列", "二叉搜索树"]),
            "interviewer_perspective": "考察基本的数据结构知识和编程能力。",
            "views": 3100,
            "stars": 285
        },

        # === 通用问题 ===
        {
            "title": "介绍一个你负责的项目，遇到的技术难点和解决方案？",
            "description": "项目经验和问题解决能力考察。",
            "category": "通用问题",
            "sub_category": "项目经验",
            "difficulty": "中等",
            "tags": json.dumps(["项目经验", "技术难点", "问题解决"]),
            "answer": """回答项目经验题目的结构化方法：<br><br>
<strong>1. 项目背景</strong><br>
- 项目规模和团队大小<br>
- 业务背景和目标<br>
- 技术栈选择原因<br><br>
<strong>2. 个人职责</strong><br>
- 担任的角色和具体责任<br>
- 负责的模块或功能<br>
- 与团队的协作方式<br><br>
<strong>3. 技术难点</strong><br>
- 具体的技术挑战<br>
- 为什么是难点<br>
- 当时的技术限制<br><br>
<strong>4. 解决方案</strong><br>
- 分析问题的过程<br>
- 考虑的多种方案<br>
- 最终选择的方案和原因<br>
- 实施过程中的调整<br><br>
<strong>5. 结果和收获</strong><br>
- 解决问题的效果<br>
- 性能提升的具体数据<br>
- 个人技术成长<br>
- 对团队的贡献""",
            "key_points": json.dumps([
                "结构化表达，逻辑清晰",
                "突出个人贡献和技术能力",
                "用数据量化成果",
                "展现学习能力和成长mindset"
            ]),
            "related_topics": json.dumps(["STAR法则", "技术选型", "团队协作"]),
            "interviewer_perspective": "考察实际项目经验、问题解决能力和沟通表达能力。",
            "views": 4200,
            "stars": 356
        },
        {
            "title": "如何与团队成员合作？遇到分歧如何处理？",
            "description": "团队协作和沟通能力考察。",
            "category": "通用问题",
            "sub_category": "团队协作",
            "difficulty": "简单",
            "tags": json.dumps(["团队协作", "沟通", "冲突处理"]),
            "answer": """团队合作和分歧处理的方法：<br><br>
<strong>日常合作原则：</strong><br>
1. <strong>主动沟通</strong>：及时同步进度和问题<br>
2. <strong>明确分工</strong>：清楚各自的职责边界<br>
3. <strong>互相支持</strong>：在他人遇到困难时主动帮助<br>
4. <strong>知识分享</strong>：定期分享技术心得<br><br>
<strong>分歧处理策略：</strong><br>
1. <strong>倾听理解</strong>：认真听取对方观点<br>
2. <strong>数据支撑</strong>：用事实和数据说话<br>
3. <strong>寻找共同点</strong>：找到双方认同的目标<br>
4. <strong>实验验证</strong>：通过小规模测试验证方案<br>
5. <strong>上级协调</strong>：必要时寻求上级帮助<br><br>
<strong>具体实例：</strong><br>
- 技术方案分歧：通过原型验证优劣<br>
- 进度安排分歧：重新评估需求优先级<br>
- 代码规范分歧：制定团队统一标准""",
            "key_points": json.dumps([
                "展现成熟的沟通协作能力",
                "用具体事例说明处理方式",
                "体现以解决问题为导向的思维",
                "展示团队意识和大局观"
            ]),
            "related_topics": json.dumps(["沟通技巧", "冲突管理", "团队文化"]),
            "interviewer_perspective": "考察团队协作能力、沟通技巧和处理人际关系的成熟度。",
            "views": 2890,
            "stars": 234
        },
        {
            "title": "你的职业规划是什么？",
            "description": "职业发展和个人规划相关问题。",
            "category": "通用问题",
            "sub_category": "职业规划",
            "difficulty": "简单",
            "tags": json.dumps(["职业规划", "个人发展", "目标"]),
            "answer": """职业规划的回答框架：<br><br>
<strong>短期目标（1-2年）：</strong><br>
- 技术能力提升的具体方向<br>
- 希望参与的项目类型<br>
- 想要掌握的新技术<br>
- 在团队中的角色发展<br><br>
<strong>中期目标（3-5年）：</strong><br>
- 技术专家或管理方向的选择<br>
- 行业深度或技术广度的权衡<br>
- 希望承担的更大责任<br>
- 对公司和团队的贡献<br><br>
<strong>长期愿景（5年以上）：</strong><br>
- 在行业中的定位<br>
- 技术影响力的建设<br>
- 可能的创业或转型方向<br><br>
<strong>与公司的契合：</strong><br>
- 了解公司的发展方向<br>
- 个人成长与公司发展的结合点<br>
- 能为公司带来的价值<br><br>
<strong>学习和提升计划：</strong><br>
- 持续学习的习惯<br>
- 参与开源项目或技术社区<br>
- 考取相关认证或学位""",
            "key_points": json.dumps([
                "目标明确且具有可操作性",
                "展现对行业和技术趋势的理解",
                "体现持续学习和自我提升的意识",
                "与应聘公司的发展方向契合"
            ]),
            "related_topics": json.dumps(["个人品牌", "技术成长路径", "行业趋势"]),
            "interviewer_perspective": "了解候选人的职业目标、学习动机和与公司的匹配度。",
            "views": 3567,
            "stars": 289
        }
    ]
    
    for q_data in questions_data:
        existing = db.query(Question).filter(
            Question.title == q_data["title"]
        ).first()
        
        if not existing:
            question = Question(**q_data)
            db.add(question)
    
    db.commit()
    print("✅ 题目数据初始化完成")

def main():
    """主函数"""
    db = SessionLocal()
    try:
        print("开始初始化知识库数据...")
        init_categories(db)
        init_questions(db)
        print("🎉 知识库数据初始化完成！")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()