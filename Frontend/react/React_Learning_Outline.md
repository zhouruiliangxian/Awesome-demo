 # React 学习大纲：从入门到精通

 ## 一、React 基础 (Fundamentals)

 1.  **React 是什么？**

     *   了解 React 的核心思想：声明式、组件化、一次学习，随处编写。

     *   理解虚拟 DOM (Virtual DOM) 的工作原理。

 2.  **环境搭建**

     *   使用 `Vite` 或 `Create React App` 快速创建项目。

     *   熟悉项目结构：`src`, `public`, `package.json` 等。

 3.  **JSX 语法**

     *   在 JavaScript 中编写类似 HTML 的代码。

     *   嵌入表达式 `{}`。

     *   JSX 属性 (Attributes) 与 CSS 类名 (`className`)。

 4.  **组件 (Components)**

     *   **函数组件 (Functional Components)**：现代 React 的标准方式。

     *   **类组件 (Class Components)**：理解基本概念，能看懂老代码即可。

     *   组件的导入与导出 (Import/Export)。

 5.  **Props vs. State**

     *   **Props**：父组件向子组件传递数据，只读。

     *   **State**：组件内部自身的状态，可变。使用 `useState` Hook 管理。

 6.  **事件处理 (Handling Events)**

     *   绑定事件处理器，如 `onClick`, `onChange`。

     *   在事件处理函数中传递参数。

 7.  **条件渲染 (Conditional Rendering)**

     *   使用 `if/else`、三元运算符 `? :`、逻辑与 `&&` 操作符。

 8.  **列表与 Keys**

     *   使用 `.map()` 方法渲染列表数据。

     *   理解 `key` 属性的重要性，用于高效的 DOM 更新。

 ## 二、React 核心 Hooks

 1.  **`useState`**

     *   在函数组件中添加和管理 state。

 2.  **`useEffect`**

     *   处理副作用，如数据获取、DOM 操作、订阅等。

     *   理解其依赖项数组 `[]` 的作用，控制副作用的执行时机。

 3.  **`useContext`**

     *   在组件树中进行跨层级的状态共享，避免 “Props 钻孔 (Prop Drilling)”。

 4.  **`useReducer`**

     *   用于更复杂的状态逻辑管理，是 `useState` 的替代方案。

 5.  **`useRef`**

     *   获取 DOM 元素的引用。

     *   存储不触发重新渲染的可变值。

 6.  **性能优化 Hooks**

     *   **`useMemo`**：缓存计算结果。

     *   **`useCallback`**：缓存函数本身。

     *   **`React.memo`**：缓存组件的渲染结果。

 7.  **自定义 Hooks (Custom Hooks)**

     *   将组件逻辑提取到可重用的函数中，实现逻辑共享。

 ## 三、React 高级概念

 1.  **路由 (Routing)**

     *   使用 `React Router` 实现单页应用 (SPA) 的页面导航。

     *   动态路由、嵌套路由、路由守卫。

 2.  **状态管理 (State Management)**

     *   **Redux / Redux Toolkit**：经典的企业级状态管理库。

     *   **Zustand / Jotai**：更轻量、现代的状态管理方案。

 3.  **与后端 API 通信**

     *   使用 `fetch` 或 `axios` 进行数据请求。

     *   使用 `React Query` 或 `SWR` 管理服务器状态，简化数据获取、缓存和同步。

 4.  **表单处理**

     *   受控组件 (Controlled Components) 与非受控组件 (Uncontrolled Components)。

     *   使用 `React Hook Form` 或 `Formik` 简化复杂的表单逻辑和校验。

 5.  **测试 (Testing)**

     *   使用 `Jest` 作为测试运行器。

     *   使用 `React Testing Library` 编写面向用户的单元测试和集成测试。

 ## 四、生态系统与工具

 1.  **React 框架**

     *   **Next.js**：生产级的 React 框架，支持服务端渲染 (SSR)、静态站点生成 (SSG) 等。

     *   **Remix**：专注于 Web 基础和现代用户体验的框架。

 2.  **UI 组件库**

     *   **Material-UI (MUI)**

     *   **Ant Design**

     *   **Tailwind CSS**：一种功能优先的 CSS 框架，与 React 结合使用非常流行。

 3.  **TypeScript**

     *   在 React 项目中加入静态类型，提升代码健壮性和可维护性。

 ## 五、学习资源推荐

 *   **官方文档**：[react.dev](https://react.dev/) - 最权威、最准确的学习资料。

 *   **在线课程**：Codecademy, freeCodeCamp, Scrimba 等平台提供了优秀的交互式教程。

 *   **实战项目建议**：

     *   待办事项列表 (Todo List)

     *   天气应用

     *   博客平台

     *   简单的电商网站
