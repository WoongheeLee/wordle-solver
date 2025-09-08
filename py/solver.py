import random
import re


class WordleSolver:

    def __init__(self, 
                 path_vocab='../dictionary/full_vocabs.txt',
                 path_unique='../dictionary/unique.txt'
                ):
        # Load all dictionary files into a set
        self.all_words = self._load_all_dictionaries()
        self.vocabs = list(self.all_words)  # Convert set to list for compatibility
        self.unique = self._get_words(path_unique)
        self.flag_first = True
        self.no = set() # 절대 안들어가는 알파벳
        self.yes = [None] * 5 # 위치도 맞아떨어지는 알파벳
        self.wrong = set() # 들어가는 알파벳인데 위치 틀림
        self.update_wrong = list()
        self.including = set()

        print('Initialized with', len(self.vocabs), 'words.')
    
    def _get_words(self, fname):
        '''
        args
            fname: (str) 읽어올 파일 경로
        returns
            (list) 단어
        '''
        with open(fname, 'r') as f:
            lines = f.readlines()
            words = [line.strip() for line in lines]
        return words
    
    def _load_all_dictionaries(self):
        '''
        Load all dictionary files and combine them into a set
        returns
            (set) 모든 사전의 단어들
        '''
        import os
        import glob
        
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dict_dir = os.path.join(current_dir, '..', 'dictionary')
        dict_dir = os.path.normpath(dict_dir)
        
        all_words = set()
        
        # Find all .txt files in dictionary directory
        pattern = os.path.join(dict_dir, '*.txt')
        dict_files = glob.glob(pattern)
        
        print(f'Loading dictionaries from: {dict_dir}')
        
        for dict_file in dict_files:
            try:
                with open(dict_file, 'r', encoding='utf-8') as f:
                    words = [line.strip().lower() for line in f.readlines() if line.strip()]
                    # Filter for 5-letter words only
                    five_letter_words = [word for word in words if len(word) == 5 and word.isalpha()]
                    all_words.update(five_letter_words)
                    print(f'Loaded {len(five_letter_words)} words from {os.path.basename(dict_file)}')
            except Exception as e:
                print(f'Error loading {dict_file}: {e}')
        
        print(f'Total unique 5-letter words: {len(all_words)}')
        return all_words


    def _exclude_letters(self):
        '''
        제외 알파벳 들어가는 단어 빼
        '''
        filtered = set()
        for v in self.vocabs:
            check = True
            for n in self.no:
                if n in v:
                    check = False
                    break
            if check:
                filtered.add(v)
        self.vocabs = sorted(filtered)


    def _match_exact(self):
        '''
        (list) 맞아떨어지는 단어장
        '''
        pattern = '^'
        for y in self.yes:
            if y: 
                pattern += f"{y}"
            else:
                pattern += '.'
        # 전체 5글자 일치 보장
        pattern += '$'
        filtered = set()
        for v in self.vocabs:
            if re.match(pattern, v):
                filtered.add(v)

        self.vocabs = sorted(filtered)

    def _filter_misplaced(self):
        '''
        노란색(wrong position) 글자들로 필터링
        '''
        # update_wrong에서 wrong 패턴들을 처리
        while self.update_wrong:
            wrong = self.update_wrong.pop()
            for i, letter in enumerate(wrong):
                if letter:
                    # 해당 위치에 해당 글자가 오면 안됨
                    placeholder = [None] * 5
                    placeholder[i] = letter
                    self.wrong.add(tuple(placeholder))
                    # 하지만 단어에는 포함되어야 함
                    self.including.add(letter)

        # 필터링 수행
        filtered = []
        for word in self.vocabs:
            valid = True
            
            # 1. including의 모든 글자가 포함되어야 함
            for required_letter in self.including:
                if required_letter.lower() not in word.lower():
                    valid = False
                    break
            
            if not valid:
                continue
                
            # 2. wrong 위치에는 해당 글자가 오면 안됨
            for wrong_pattern in self.wrong:
                for pos, forbidden_letter in enumerate(wrong_pattern):
                    if forbidden_letter and len(word) > pos:
                        if word[pos].lower() == forbidden_letter.lower():
                            valid = False
                            break
                if not valid:
                    break
                    
            if valid:
                filtered.append(word)
                
        self.vocabs = sorted(filtered)


    def _update_exclude(self):
        '''
        args
            no: (set) 절대 안들어가는 알파벳
        '''
        # 이미 확정된 초록(yes) 글자는 제외 집합에서 제거
        yes_letters = {c for c in self.yes if c}
        self.no = set(self.no) - yes_letters
        self._exclude_letters()
        print('excluding:', sorted(self.no))

    
    def _update_exact(self):
        '''
        args
            yes: (list) 위치 맞아떨어지는 알파벳
        '''
        self._match_exact()

    def _update_misplaced(self):
        ''' 
        args
            wrong: (list) 위치 틀린 알파벳
        '''
        self._filter_misplaced()
    

    def _rank_by_frequency(self, candidates, alpha=0.5, dup_penalty=0.25):
        '''
        남은 후보를 문자/자리 빈도 기반으로 스코어링하여 내림차순 정렬 반환
        '''
        # 빈도 집계
        letter_freq = {chr(c): 0 for c in range(ord('a'), ord('z')+1)}
        pos_freq = [dict() for _ in range(5)]

        for w in self.vocabs:
            seen = set()
            for i, ch in enumerate(w):
                # 위치별 빈도
                pos_freq[i][ch] = pos_freq[i].get(ch, 0) + 1
                # 글자 빈도는 단어 내 중복은 1회만 카운트
                if ch not in seen:
                    letter_freq[ch] += 1
                    seen.add(ch)

        def score(word):
            uniq = set(word)
            # 전역 글자 빈도 합 + 자리별 빈도 가중치
            s = sum(letter_freq.get(ch, 0) for ch in uniq)
            s += alpha * sum(pos_freq[i].get(word[i], 0) for i in range(5))
            # 중복 패널티
            s -= dup_penalty * (len(word) - len(uniq))
            return s

        ranked = sorted(candidates, key=score, reverse=True)
        return ranked


    def sample_word(self, yes=None, wrong=None, no=None, flag=True, itr=5, strategy='random'):
        '''
        정답일 것 같은 단어 추천
        
        args
            yes: (list) 위치 맞아떨어지는 알파벳
            wrong: (list) 위치 틀린데 들어가는 알파벳
            no: (set, list) 절대 안들어가는 알파벳
            flag: (bool) 첫 시도냐(true) 아니냐(false)
            itr: (int) 추천 단어 개수
            strategy: (str) 'random' 또는 'freq'
        '''
        print('sampling...')
        if yes:
            assert len(yes) == 5
        if wrong:
            assert len(wrong) == 5
            
        if yes:
            for i, v in enumerate(yes):
                if yes[i]:
                    self.yes[i] = yes[i]
            self._update_exact()
        if wrong:
            self.update_wrong.append(wrong)
            self._update_misplaced()
        if no:
            self.no = self.no | no
            self._update_exclude()

        solutions = dict()
        suggestions = []

        candidates = self.vocabs
        if strategy == 'random':
            if self.flag_first and flag:
                # 첫 라운드면 unique에서 랜덤 추천
                for _ in range(min(itr, len(self.unique))):
                    idx = int(random.random() * len(self.unique))
                    suggestions.append(self.unique[idx])
                self.flag_first = False
            else:
                print('vocabs:', len(self.vocabs))
                for _ in range(min(itr, len(self.vocabs))):
                    idx = int(random.random() * len(self.vocabs))
                    suggestions.append(self.vocabs[idx])
        elif strategy == 'freq':
            # 빈도 기반 스코어 상위 반환
            ranked = self._rank_by_frequency(candidates)
            suggestions = ranked[:itr]
            self.flag_first = False
        else:
            # 알 수 없는 전략은 랜덤으로 폴백
            print(f"Unknown strategy '{strategy}', fallback to random")
            for _ in range(min(itr, len(self.vocabs))):
                idx = int(random.random() * len(self.vocabs))
                suggestions.append(self.vocabs[idx])

        print('# of words:', len(self.vocabs))

        # 결과가 없을 때 정확히 알려주기
        if len(self.vocabs) == 0:
            print("No words match all conditions!")
            solutions['word_nums'] = 0
            solutions['suggestions'] = []
            solutions['no_results'] = True
            solutions['message'] = "조건을 모두 만족하는 단어가 사전에 없습니다. 이전 시도의 색상 설정을 확인하거나, 더 많은 단어가 포함된 사전이 필요할 수 있습니다."
        else:
            solutions['word_nums'] = len(self.vocabs)
            solutions['suggestions'] = suggestions
            solutions['no_results'] = False
            
        return solutions
