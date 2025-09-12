#!/usr/bin/env python3
"""
意图路由系统 - 智能识别用户查询意图并路由到对应Agent
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SkillType(Enum):
    """技能类型枚举"""
    PROCESS = "process"      # 办事流程
    COURSE = "course"        # 课程学习
    CONTACT = "contact"      # 联系人查询
    POLICY = "policy"        # 政策条款
    GREETING = "greeting"    # 问候闲聊
    UNKNOWN = "unknown"      # 未知意图

@dataclass
class IntentResult:
    """意图识别结果"""
    skill: SkillType
    confidence: float
    entities: Dict[str, Any]
    filters: List[str]
    original_query: str
    processed_query: str

class IntentRouter:
    """意图路由器 - 核心路由逻辑"""
    
    def __init__(self):
        self.skill_patterns = self._init_skill_patterns()
        self.entity_patterns = self._init_entity_patterns()
        self.stop_words = self._init_stop_words()
    
    def _init_skill_patterns(self) -> Dict[SkillType, List[str]]:
        """初始化技能匹配模式"""
        return {
            SkillType.PROCESS: [
                # 报销相关
                r'报销', r'医疗', r'医药费', r'看病', r'就医', r'住院', r'门诊',
                r'发票', r'转诊', r'急诊', r'寒暑假', r'到账', r'周期', r'截止',
                
                # 办事流程（具体事务）
                r'学籍', r'注册', r'休学', r'复学', r'转学', r'退学',
                r'宿舍', r'住宿', r'调换', r'退宿',
                r'成绩单', r'在读证明', r'毕业证明', r'学位证明',
                r'盖章', r'审核', r'手续'
            ],
            
            SkillType.COURSE: [
                # 课程相关
                r'课程', r'选课', r'退课', r'调课', r'课表', r'上课',
                r'学分', r'学时', r'必修', r'选修', r'公选', r'专业课',
                
                # 成绩相关
                r'成绩', r'分数', r'绩点', r'GPA', r'排名', r'查询',
                r'补考', r'重修', r'缓考', r'免修',
                
                # 考试相关
                r'考试', r'期末', r'期中', r'四六级', r'计算机', r'普通话',
                r'报名', r'缴费', r'准考证', r'考场', r'时间',
                
                # 学习相关
                r'学习', r'作业', r'实验', r'实习', r'论文', r'答辩',
                
                # 升学规划相关
                r'保研', r'考研', r'留学', r'申请', r'升学', r'规划',
                r'PhD', r'硕士', r'博士', r'直博', r'MPhil', r'MRes',
                
                # 职业发展相关
                r'职业', r'发展', r'规划', r'方向', r'选择', r'路径',
                r'CS', r'计算机', r'软件', r'AI', r'人工智能',
                
                # 科研相关
                r'科研', r'项目', r'大创', r'竞赛', r'导师', r'套磁',
                r'论文', r'会议', r'发表', r'成果', r'展示',
                
                # 学习资源相关
                r'自学', r'资源', r'教程', r'课程', r'GitHub', r'开源',
                r'Coursera', r'LeetCode', r'编程', r'技能', r'提升'
            ],
            
            SkillType.CONTACT: [
                # 联系人查询
                r'老师', r'教授', r'导师', r'辅导员', r'班主任',
                r'联系', r'电话', r'邮箱', r'微信', r'QQ',
                r'办公', r'办公室', r'地点', r'地址', r'在哪',
                
                # 部门查询
                r'部门', r'学院', r'教务处', r'学生处', r'财务处',
                r'图书馆', r'医务室', r'保卫处', r'后勤',
                
                # 窗口查询
                r'窗口', r'服务', r'咨询', r'办理', r'时间', r'开放'
            ],
            
            SkillType.POLICY: [
                # 政策条款
                r'政策', r'规定', r'制度', r'条例', r'办法', r'细则',
                r'标准', r'要求', r'条件', r'资格', r'限制',
                
                # 规章制度
                r'校规', r'纪律', r'处分', r'奖励', r'奖学金', r'助学金',
                r'勤工助学', r'贷款', r'减免',
                
                # 比例、金额
                r'比例', r'百分比', r'金额', r'费用', r'收费', r'标准'
            ],
            
            SkillType.GREETING: [
                r'你好', r'早上好', r'中午好', r'下午好', r'晚上好',
                r'嗨', r'hi', r'hello', r'谢谢', r'感谢', r'再见', r'拜拜',
                r'小医', r'助手', r'帮助', r'介绍', r'功能'
            ]
        }
    
    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        """初始化实体识别模式"""
        return {
            'hospital': [
                r'中心医院', r'市立医院', r'南海新区医院', r'校医务室',
                r'威海中心', r'威海市立', r'南海医院'
            ],
            'dept': [
                r'教务处', r'学生处', r'财务处', r'图书馆', r'医务室',
                r'保卫处', r'后勤处', r'信息中心', r'网络中心'
            ],
            'type': [
                r'门诊', r'住院', r'急诊', r'体检', r'检查', r'治疗'
            ],
            'time': [
                r'寒暑假', r'学期', r'学年', r'周', r'月', r'年',
                r'工作日', r'周末', r'节假日'
            ],
            'amount': [
                r'\d+%', r'\d+元', r'\d+块', r'\d+毛', r'几百', r'几千'
            ]
        }
    
    def _init_stop_words(self) -> set:
        """初始化停用词"""
        return {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
            '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
            '着', '没有', '看', '好', '自己', '这', '那', '吗', '么', '什么',
            '怎么', '可以', '这个', '那个', '能', '为', '吧', '啊', '呢', '呀'
        }
    
    def detect_intent(self, query: str) -> IntentResult:
        """检测用户意图"""
        # 预处理查询
        processed_query = self._preprocess_query(query)
        
        # 计算各技能的匹配分数
        skill_scores = {}
        for skill, patterns in self.skill_patterns.items():
            score = self._calculate_skill_score(processed_query, patterns)
            skill_scores[skill] = score
        
        # 选择最高分的技能
        best_skill = max(skill_scores.items(), key=lambda x: x[1])
        skill_type, confidence = best_skill
        
        # 如果最高分太低，使用通用对话处理
        if confidence < 0.1:
            skill_type = SkillType.GREETING
            confidence = 0.5
        
        # 提取实体
        entities = self._extract_entities(processed_query)
        
        # 生成过滤器
        filters = self._generate_filters(entities, skill_type)
        
        return IntentResult(
            skill=skill_type,
            confidence=confidence,
            entities=entities,
            filters=filters,
            original_query=query,
            processed_query=processed_query
        )
    
    def _preprocess_query(self, query: str) -> str:
        """预处理查询文本"""
        # 转换为小写
        query = query.lower()
        
        # 移除标点符号
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # 移除多余空格
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _calculate_skill_score(self, query: str, patterns: List[str]) -> float:
        """计算技能匹配分数"""
        total_score = 0.0
        matched_patterns = 0
        
        for pattern in patterns:
            if re.search(pattern, query):
                # 完全匹配给高分
                if re.fullmatch(pattern, query):
                    total_score += 2.0
                else:
                    total_score += 1.0
                matched_patterns += 1
        
        # 归一化分数
        if matched_patterns == 0:
            return 0.0
        
        # 考虑匹配密度
        density = matched_patterns / len(patterns)
        base_score = total_score / matched_patterns
        
        return min(base_score * (1 + density), 1.0)
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """提取实体信息"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    entities[entity_type] = match.group()
                    break
        
        return entities
    
    def _generate_filters(self, entities: Dict[str, Any], skill: SkillType) -> List[str]:
        """生成检索过滤器"""
        filters = []
        
        # 基于实体生成过滤器
        if 'hospital' in entities:
            filters.append('hospital')
        if 'dept' in entities:
            filters.append('dept')
        if 'type' in entities:
            filters.append('type')
        if 'time' in entities:
            filters.append('time')
        
        # 基于技能类型生成过滤器
        if skill == SkillType.PROCESS:
            filters.extend(['procedure', 'materials', 'contacts'])
        elif skill == SkillType.COURSE:
            filters.extend(['enrollment', 'grades', 'exams'])
        elif skill == SkillType.CONTACT:
            filters.extend(['teachers', 'departments', 'offices'])
        elif skill == SkillType.POLICY:
            filters.extend(['policies', 'regulations', 'standards'])
        
        return list(set(filters))  # 去重
    
    def get_skill_description(self, skill: SkillType) -> str:
        """获取技能描述"""
        descriptions = {
            SkillType.PROCESS: "办事流程助手 - 处理报销、申请、办理等事务",
            SkillType.COURSE: "课程学习助手 - 处理选课、成绩、考试等学习事务",
            SkillType.CONTACT: "联系人助手 - 查询老师、部门、窗口信息",
            SkillType.POLICY: "政策助手 - 解释规章制度、政策条款",
            SkillType.GREETING: "问候助手 - 处理日常问候和闲聊",
            SkillType.UNKNOWN: "通用助手 - 处理一般性查询"
        }
        return descriptions.get(skill, "未知技能")

# 全局路由器实例
intent_router = IntentRouter()

def route_query(query: str) -> IntentResult:
    """路由查询到对应技能"""
    return intent_router.detect_intent(query)

# 测试函数
def test_intent_router():
    """测试意图路由器"""
    test_queries = [
        "感冒药能报销吗？",
        "怎么申请宿舍？",
        "常春艳老师电话多少？",
        "报销比例是多少？",
        "你好，小医",
        "选课系统怎么用？",
        "成绩什么时候出来？",
        "图书馆开放时间？"
    ]
    
    print("🧪 意图路由器测试")
    print("=" * 50)
    
    for query in test_queries:
        result = route_query(query)
        print(f"查询: {query}")
        print(f"技能: {result.skill.value} (置信度: {result.confidence:.2f})")
        print(f"实体: {result.entities}")
        print(f"过滤器: {result.filters}")
        print(f"描述: {intent_router.get_skill_description(result.skill)}")
        print("-" * 30)

if __name__ == "__main__":
    test_intent_router()
