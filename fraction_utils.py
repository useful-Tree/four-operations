"""
分数工具类
处理真分数、带分数的生成、转换和运算
"""

import random
from fractions import Fraction
import math


class FractionUtils:
    """分数工具类，处理真分数和带分数相关操作"""
    
    @staticmethod
    def gcd(a, b):
        """计算最大公约数"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a, b):
        """计算最小公倍数"""
        return abs(a * b) // FractionUtils.gcd(a, b)
    
    @staticmethod
    def generate_proper_fraction(max_value):
        """
        生成真分数（分子小于分母）
        
        Args:
            max_value: 分子和分母的最大值（不包含）
            
        Returns:
            Fraction: 真分数对象
        """
        if max_value <= 1:
            return Fraction(1, 2)
            
        # 生成分母（至少为2）
        denominator = random.randint(2, max_value - 1)
        # 生成分子（小于分母）
        numerator = random.randint(1, denominator - 1)
        
        # 化简分数
        gcd_val = FractionUtils.gcd(numerator, denominator)
        numerator //= gcd_val
        denominator //= gcd_val
        
        return Fraction(numerator, denominator)
    
    @staticmethod
    def generate_mixed_number(max_value):
        """
        生成带分数
        
        Args:
            max_value: 整数部分和分数部分的最大值
            
        Returns:
            Fraction: 带分数转换后的假分数
        """
        if max_value <= 2:
            return FractionUtils.generate_proper_fraction(max_value)
            
        # 整数部分
        whole_part = random.randint(1, max_value - 2)
        # 分数部分
        fraction_part = FractionUtils.generate_proper_fraction(max_value)
        
        return Fraction(whole_part) + fraction_part
    
    @staticmethod
    def generate_number(max_value, allow_mixed=True):
        """
        生成数字（自然数或分数）
        
        Args:
            max_value: 数值范围
            allow_mixed: 是否允许带分数
            
        Returns:
            Fraction: 生成的数字
        """
        choice = random.randint(1, 4)
        
        if choice == 1:  # 自然数
            return Fraction(random.randint(0, max_value - 1))
        elif choice == 2:  # 真分数
            return FractionUtils.generate_proper_fraction(max_value)
        elif choice == 3 and allow_mixed:  # 带分数
            return FractionUtils.generate_mixed_number(max_value)
        else:  # 默认真分数
            return FractionUtils.generate_proper_fraction(max_value)
    
    @staticmethod
    def fraction_to_string(frac):
        """
        将分数转换为字符串格式
        
        Args:
            frac: Fraction对象
            
        Returns:
            str: 格式化的分数字符串
        """
        if frac.denominator == 1:
            return str(frac.numerator)
        
        # 检查是否为带分数
        if frac.numerator > frac.denominator:
            whole_part = frac.numerator // frac.denominator
            remainder = frac.numerator % frac.denominator
            if remainder == 0:
                return str(whole_part)
            else:
                return f"{whole_part}'{remainder}/{frac.denominator}"
        else:
            return f"{frac.numerator}/{frac.denominator}"
    
    @staticmethod
    def string_to_fraction(s):
        """
        将字符串转换为分数
        
        Args:
            s: 分数字符串
            
        Returns:
            Fraction: 分数对象
        """
        s = s.strip()
        
        # 处理带分数格式 "2'3/8"
        if "'" in s:
            parts = s.split("'")
            whole_part = int(parts[0])
            frac_part = parts[1]
            if "/" in frac_part:
                num, den = map(int, frac_part.split("/"))
                return Fraction(whole_part * den + num, den)
            else:
                return Fraction(whole_part)
        
        # 处理普通分数格式 "3/8"
        elif "/" in s:
            num, den = map(int, s.split("/"))
            return Fraction(num, den)
        
        # 处理整数
        else:
            return Fraction(int(s))
    
    @staticmethod
    def is_valid_subtraction(a, b):
        """
        检查减法是否有效（不产生负数）
        
        Args:
            a, b: Fraction对象
            
        Returns:
            bool: 是否有效
        """
        return a >= b
    
    @staticmethod
    def is_valid_division(a, b):
        """
        检查除法是否有效（结果为真分数）
        
        Args:
            a, b: Fraction对象
            
        Returns:
            bool: 是否有效
        """
        if b == 0:
            return False
        
        result = a / b
        # 结果必须是真分数（小于1）
        return 0 < result < 1
    
    @staticmethod
    def calculate_expression(expr_str):
        """
        计算表达式的值
        
        Args:
            expr_str: 表达式字符串
            
        Returns:
            Fraction: 计算结果
        """
        # 替换运算符为Python可识别的格式
        expr_str = expr_str.replace('×', '*').replace('÷', '/')
        
        # 处理分数格式
        tokens = []
        i = 0
        current_token = ""
        
        while i < len(expr_str):
            char = expr_str[i]
            if char in "+-*/()":
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
                if char in "+-*/":
                    tokens.append(f" {char} ")
                else:
                    tokens.append(char)
            elif char == " ":
                if current_token.strip():
                    tokens.append(current_token.strip())
                    current_token = ""
            else:
                current_token += char
            i += 1
        
        if current_token.strip():
            tokens.append(current_token.strip())
        
        # 转换分数格式
        processed_tokens = []
        for token in tokens:
            token = token.strip()
            if token and token not in "+-*/()":
                try:
                    frac = FractionUtils.string_to_fraction(token)
                    processed_tokens.append(f"Fraction({frac.numerator}, {frac.denominator})")
                except:
                    processed_tokens.append(token)
            else:
                processed_tokens.append(token)
        
        expr_str = "".join(processed_tokens)
        
        try:
            # 在安全的环境中计算表达式
            result = eval(expr_str, {"__builtins__": {}, "Fraction": Fraction})
            return result
        except:
            return Fraction(0)